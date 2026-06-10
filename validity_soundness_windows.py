"""
This file generates validity and soundness scores
Only works on Windows systems because it uses msvcrt for keyboard input and ctypes for worker memory containment
"""

import argparse
import contextlib
import csv
import ctypes
import functools
import gc
import msvcrt   # Windows-only: non-blocking keyboard input for pause/resume
import sys
import threading
import time
import warnings
from ctypes import wintypes
from multiprocessing import Manager, Pool, cpu_count
from pathlib import Path

from hypothesis import HealthCheck, Phase, assume, given, settings
from hypothesis import strategies as st
from hypothesis.errors import StopTest, Unsatisfiable
from hypothesis.reporting import with_reporter
from hypothesis.strategies import SearchStrategy
from openpyxl import Workbook
from tqdm import tqdm

PROPTESTS_DIR = Path(__file__).parent / "proptests"
TOTAL_RUNS = 1000

# ---------------------------------------------------------------------------
# Per-worker memory containment (Windows-only, ctypes — no extra dependencies).
#
# Some generated tests use a drawn integer as an allocation size (bytes(n),
# 'x'*n, np.zeros(n), ...). Because the counting wrappers swallow every
# exception so all examples run, such a test attempts huge allocations up to
# TOTAL_RUNS times — across several workers at once this exhausted the whole
# machine. Containment is layered:
#   hard cap  — a Job Object limits each worker's commit charge; VirtualAlloc
#               past the cap fails, Python raises MemoryError, the wrappers
#               count it as a validity error and the run continues. The
#               process is NOT killed.
#   soft bail — between examples the wrapper checks its own commit; if it
#               stays above soft_frac * cap even after gc.collect(), the rest
#               of the current function's budget is charged as validity
#               errors so a bloated heap can't poison subsequent functions.
#
# NOTE: validity numbers are environment-dependent under the cap. The
# mem_charged column counts exactly how many of a row's validity errors were
# memory-induced — rows with mem_charged == 0 are cap-independent.
# ---------------------------------------------------------------------------

DEFAULT_MEM_CAP_GB = 8.0
DEFAULT_SOFT_FRAC = 0.65
DEFAULT_MAXTASKSPERCHILD = 16
_MEM_CHECK_EVERY = 50    # examples between commit-size checks

# Set by _worker_init in each pool worker; stay at defaults in the parent.
_SOFT_LIMIT_BYTES: int | None = None   # None = soft guard disabled
_JOB_CAP_APPLIED = False
_JOB_HANDLE = None                     # keep the job object alive for process lifetime
_CAP_WARNING_EMITTED = False           # one cap-unavailable warning per worker


class _MemoryBudgetExceeded(BaseException):
    """Raised by the counting wrapper when the worker's commit stays above the
    soft limit even after gc.collect(). BaseException so neither the wrapper's
    `except Exception` nor Hypothesis's failure-catching intercepts it; it
    propagates out of counting_wrapped() to run_test_file's retry loop."""


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [("ReadOperationCount",  ctypes.c_uint64),
                ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64),
                ("ReadTransferCount",   ctypes.c_uint64),
                ("WriteTransferCount",  ctypes.c_uint64),
                ("OtherTransferCount",  ctypes.c_uint64)]


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                ("PerJobUserTimeLimit",     wintypes.LARGE_INTEGER),
                ("LimitFlags",              wintypes.DWORD),
                ("MinimumWorkingSetSize",   ctypes.c_size_t),
                ("MaximumWorkingSetSize",   ctypes.c_size_t),
                ("ActiveProcessLimit",      wintypes.DWORD),
                ("Affinity",                ctypes.c_size_t),   # ULONG_PTR
                ("PriorityClass",           wintypes.DWORD),
                ("SchedulingClass",         wintypes.DWORD)]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo",                _IO_COUNTERS),
                ("ProcessMemoryLimit",    ctypes.c_size_t),
                ("JobMemoryLimit",        ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed",     ctypes.c_size_t)]


class _PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", wintypes.DWORD),
                ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_uint64),
                ("ullAvailPhys", ctypes.c_uint64),
                ("ullTotalPageFile", ctypes.c_uint64),
                ("ullAvailPageFile", ctypes.c_uint64),
                ("ullTotalVirtual", ctypes.c_uint64),
                ("ullAvailVirtual", ctypes.c_uint64),
                ("ullAvailExtendedVirtual", ctypes.c_uint64)]


_JobObjectExtendedLimitInformation = 9
_JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.CreateJobObjectW.restype = wintypes.HANDLE
_k32.GetCurrentProcess.restype = wintypes.HANDLE
_k32.SetInformationJobObject.argtypes = [
    wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
]
_k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
_k32.CloseHandle.argtypes = [wintypes.HANDLE]
_k32.GlobalMemoryStatusEx.argtypes = [ctypes.c_void_p]

_psapi = ctypes.WinDLL("psapi", use_last_error=True)
_psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]


def _apply_job_memory_cap(cap_bytes: int) -> bool:
    """Cap this process's commit charge via an anonymous Job Object.

    JOB_OBJECT_LIMIT_PROCESS_MEMORY limits committed (private) bytes, not the
    working set: any VirtualAlloc past the cap fails, CPython's allocator gets
    NULL, and Python raises MemoryError — the process keeps running. Workers
    typically already live inside a job (Windows Terminal); Windows 8+ nests
    jobs, but if assignment still fails we degrade to the soft guard only.
    """
    global _JOB_HANDLE
    hjob = _k32.CreateJobObjectW(None, None)
    if not hjob:
        return False
    info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_PROCESS_MEMORY
    info.ProcessMemoryLimit = cap_bytes
    if not _k32.SetInformationJobObject(
        hjob, _JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info)
    ):
        _k32.CloseHandle(hjob)
        return False
    if not _k32.AssignProcessToJobObject(hjob, _k32.GetCurrentProcess()):
        _k32.CloseHandle(hjob)
        return False
    _JOB_HANDLE = hjob
    return True


def _private_bytes() -> int:
    """This process's commit charge (the figure the job cap enforces)."""
    pmc = _PROCESS_MEMORY_COUNTERS_EX()
    pmc.cb = ctypes.sizeof(pmc)
    if not _psapi.GetProcessMemoryInfo(_k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
        return 0
    return pmc.PrivateUsage


def _available_phys_bytes() -> int:
    ms = _MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(ms)
    if not _k32.GlobalMemoryStatusEx(ctypes.byref(ms)):
        return 0
    return ms.ullAvailPhys


def _worker_init(cap_bytes: int | None, soft_frac: float) -> None:
    """Pool initializer — runs in every (replacement) worker, so the cap is
    re-applied automatically under maxtasksperchild recycling."""
    global _SOFT_LIMIT_BYTES, _JOB_CAP_APPLIED
    if cap_bytes is None:   # --no-mem-cap
        _SOFT_LIMIT_BYTES = None
        _JOB_CAP_APPLIED = False
        return
    _JOB_CAP_APPLIED = _apply_job_memory_cap(cap_bytes)
    _SOFT_LIMIT_BYTES = int(cap_bytes * soft_frac)


class _DevNull:
    def write(self, *a): pass
    def flush(self): pass


class _QueueWriter:
    """Routes stdout/stderr writes from a worker process through the progress queue
    so the display thread can emit them via tqdm.write(), keeping bars intact."""
    def __init__(self, queue):
        self._queue = queue
        self._buf = ""

    def write(self, text):
        self._buf += text
        # flush complete lines immediately so messages appear promptly
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                self._queue.put(("write", line))

    def flush(self):
        if self._buf.strip():
            self._queue.put(("write", self._buf))
            self._buf = ""


_GEN_CRASH = object()  # sentinel: drawing from the strategy raised an exception
_GEN_OOM = object()    # sentinel: drawing from the strategy raised MemoryError


def _safe_strategy(strategy):
    """Wrap a strategy so exceptions raised during input *generation* (broken
    .map/.filter lambdas, st.composite bodies, st.builds, ...) yield a sentinel
    instead of escaping to the engine. An escaped generation error makes
    Hypothesis abort the entire run with a "@seed(...)" message — and because a
    restarted engine re-tries minimal inputs first, a crash on a simple input
    would otherwise degenerate every retry into the same example. With the
    sentinel the engine sees a passing test and keeps exploring diversely.

    StopTest must propagate: it is engine control flow (mark_invalid, buffer
    overruns) and swallowing it would corrupt the engine. ConjectureData.draw
    closes its span in a finally block, so catching here is span-safe.
    """
    @st.composite
    def _safe(draw):
        try:
            return draw(strategy)
        except (StopTest, KeyboardInterrupt):
            raise
        except MemoryError:
            # Distinguished from _GEN_CRASH only for mem_charged accounting.
            draw(st.integers(min_value=0, max_value=2**64))
            return _GEN_OOM
        except BaseException:
            # Consume fresh entropy: a strategy that crashes before drawing any
            # choices would otherwise produce the same empty choice sequence
            # every time, and the engine would stop after one example thinking
            # the search space is exhausted.
            draw(st.integers(min_value=0, max_value=2**64))
            return _GEN_CRASH
    return _safe()


def _make_counting_runner(func):
    """
    Extract the @given strategies from func's closure, re-apply them to a non-raising
    wrapper, and return (counting_wrapped, executed, assertion_errors, other_errors,
    mem_errors) where all but the first are single-element counter lists.

    Because the inner wrapper never raises, Hypothesis never "finds" a failure in the
    test *body* and keeps generating — giving full coverage-guided exploration instead
    of n independent draws from the biased-toward-small geometric distribution.

    Exceptions raised during input *generation* (inside strategies) cannot be caught
    here; run_test_file handles those by restarting the engine with the remaining
    example budget (see the retry loop there).

    Returns None if the strategies cannot be extracted (fallback to original loop).
    """
    if not getattr(func, 'is_hypothesis_test', False):
        return None

    inner = func.hypothesis.inner_test
    given_kwargs = {
        # Leave non-strategy values (e.g. `...` for infer-from-annotation) alone.
        k: _safe_strategy(v) if isinstance(v, SearchStrategy) else v
        for k, v in func.hypothesis._given_kwargs.items()
    }

    executed = [0]
    assertion_errors = [0]
    other_errors = [0]
    mem_errors = [0]

    @functools.wraps(inner)
    def counting_inner(*args, **kwargs):
        # Soft memory guard, checked before the example is counted so a bail
        # does not consume budget. Fires on example 0 too: a function that
        # inherits a bloated heap from its predecessor bails immediately.
        if _SOFT_LIMIT_BYTES is not None and executed[0] % _MEM_CHECK_EVERY == 0:
            if _private_bytes() > _SOFT_LIMIT_BYTES:
                gc.collect()
                if _private_bytes() > _SOFT_LIMIT_BYTES:
                    raise _MemoryBudgetExceeded
        executed[0] += 1
        gen_values = list(args) + list(kwargs.values())
        if any(v is _GEN_CRASH or v is _GEN_OOM for v in gen_values):
            # Input generation crashed for this example: the input is invalid,
            # and the test body can't meaningfully run without it.
            other_errors[0] += 1
            if any(v is _GEN_OOM for v in gen_values):
                mem_errors[0] += 1
            return
        try:
            inner(*args, **kwargs)
        except AssertionError:
            assertion_errors[0] += 1
        except ExceptionGroup as eg:
            if eg.subgroup(AssertionError) is not None:
                assertion_errors[0] += 1
            if eg.subgroup(lambda e: not isinstance(e, AssertionError)) is not None:
                other_errors[0] += 1
        except MemoryError:
            other_errors[0] += 1
            mem_errors[0] += 1
        except Exception:
            other_errors[0] += 1
        except StopTest:
            # Engine control flow (e.g. buffer overrun during an interactive
            # data.draw() in the test body): the example never completed, so
            # un-count it and let the engine handle it — swallowing it would
            # corrupt the engine's state.
            executed[0] -= 1
            raise
        except KeyboardInterrupt:
            raise
        except BaseException:
            # SystemExit, GeneratorExit, BaseExceptionGroup, etc. — count and continue
            # rather than letting them escape to Hypothesis (which would print a
            # reproduction/seed message) or crash the worker process.
            other_errors[0] += 1

    counting_wrapped = given(**given_kwargs)(counting_inner)
    return counting_wrapped, executed, assertion_errors, other_errors, mem_errors


def run_test_file(
    test_path: Path, n: int = TOTAL_RUNS, progress_queue=None, task_id: str | None = None
) -> list[tuple[str, int, int, int, int]]:
    """Return a list of (test_name, total, soundness, validity, mem_charged) — one
    entry per test function. mem_charged counts how many of the validity errors
    were memory-induced (MemoryError under the worker cap, or a soft-limit bail).

    task_id must be globally unique across all concurrent workers; it is used as the key
    for progress-bar slot assignment.  Defaults to the file stem (not unique when running
    multiple models/apis in parallel — callers should always supply it).
    """
    key = task_id if task_id is not None else test_path.stem
    source = test_path.read_text(encoding="utf-8")
    namespace = {"__name__": "__main__"}

    _out = _QueueWriter(progress_queue) if progress_queue is not None else _DevNull()
    with (
        contextlib.redirect_stdout(_out),
        contextlib.redirect_stderr(_out),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("ignore")

        global _CAP_WARNING_EMITTED
        if _SOFT_LIMIT_BYTES is not None and not _JOB_CAP_APPLIED and not _CAP_WARNING_EMITTED:
            _CAP_WARNING_EMITTED = True
            print("[mem] hard memory cap unavailable in this worker; soft guard only")

        try:
            exec(compile(source, str(test_path), "exec"), namespace)
        except Exception:
            return [("<load_error>", n, n, 0, 0)]

        test_funcs = [
            (k, v) for k, v in namespace.items() if k.startswith("test_") and callable(v)
        ]

        if not test_funcs:
            return []

        if progress_queue is not None:
            progress_queue.put(("start", key, len(test_funcs)))

        results = []
        for func_name, func in test_funcs:
            runner_info = _make_counting_runner(func)

            if runner_info is not None:
                counting_wrapped, executed, ae_list, oe_list, mem_list = runner_info
                # Exceptions raised while *generating* an input (broken .map/.filter
                # lambdas, st.composite bodies, st.builds, ...) happen before
                # counting_inner runs, so the catch-all wrapper never sees them.
                # Hypothesis treats them as failures, prints a "@seed(...)" note,
                # and aborts — losing the rest of the example budget. Count each
                # abort as one invalid example and restart the engine with the
                # remaining budget until all n examples are accounted for. The
                # reporter is silenced so falsifying-example/@seed messages never
                # reach the terminal.
                engine_aborts = 0
                with with_reporter(lambda _msg: None):
                    while executed[0] + engine_aborts < n:
                        counting_wrapped._hypothesis_internal_use_settings = settings(
                            max_examples=n - executed[0] - engine_aborts,
                            deadline=None,  # counting_inner can't surface DeadlineExceeded;
                                            # the engine raises it itself after the call,
                                            # aborting the run early — disable it entirely.
                            suppress_health_check=list(HealthCheck),
                            database=None,
                            phases=[Phase.generate],
                            print_blob=False,
                        )
                        try:
                            counting_wrapped()
                        except KeyboardInterrupt:
                            raise
                        except _MemoryBudgetExceeded:
                            # Worker commit stayed above the soft limit even after
                            # gc.collect(). Must be caught BEFORE the BaseException
                            # branch: treated as an engine abort it would retry and
                            # immediately re-trigger. Charge the remaining budget as
                            # (memory-induced) validity errors and move on.
                            remaining = n - executed[0] - engine_aborts
                            oe_list[0] += remaining
                            mem_list[0] += remaining
                            print(
                                f"[mem] {test_path.name}:{func_name} over soft memory "
                                f"limit; {remaining} examples charged as validity errors"
                            )
                            break
                        except Unsatisfiable:
                            # The strategy can't produce any valid examples at all —
                            # retrying would just spin; charge the whole remaining
                            # budget as invalid and move on.
                            oe_list[0] += n - executed[0] - engine_aborts
                            break
                        except BaseException:
                            # Engine-level failure (generation error, Flaky, ...):
                            # record one invalid example and resume.
                            engine_aborts += 1
                            oe_list[0] += 1
                        else:
                            # Clean completion — the engine only stops short of
                            # max_examples if it exhausted the search space.
                            break
                assertion_errors = ae_list[0]
                other_errors = oe_list[0]
                mem_charged = mem_list[0]
            else:
                print("wrapping failed for test at",  str(test_path))
                # Fallback for non-@given or unrecognised decorator shapes.
                assertion_errors = 0
                other_errors = 0
                mem_charged = 0
                _fallback_runner = settings(
                    max_examples=1,
                    deadline=None,
                    suppress_health_check=list(HealthCheck),
                    database=None,
                    phases=[Phase.generate],
                )
                func._hypothesis_internal_use_settings = _fallback_runner
                for _ in range(n):
                    try:
                        func()
                    except AssertionError:
                        assertion_errors += 1
                    except ExceptionGroup as eg:
                        if eg.subgroup(AssertionError) is not None:
                            assertion_errors += 1
                        if eg.subgroup(lambda e: not isinstance(e, AssertionError)) is not None:
                            other_errors += 1
                    except MemoryError:
                        other_errors += 1
                        mem_charged += 1
                    except Exception:
                        other_errors += 1

            if progress_queue is not None:
                progress_queue.put(("update", key))

            soundness = n - assertion_errors
            validity = n - other_errors
            results.append((func_name, n, soundness, validity, mem_charged))

        if progress_queue is not None:
            progress_queue.put(("done", key))

        # Drop the exec'd module's globals and collect Hypothesis DataTree
        # cycles before the worker moves on to the next file.
        namespace.clear()
        gc.collect()

    return results


def _worker(args) -> list[dict]:
    model, api, stage, rep, test_path, progress_queue = args
    # Build a globally unique key so concurrent workers never collide in the display thread.
    task_id = f"{model}/{api}/{stage}/{rep}"
    func_results = run_test_file(test_path, progress_queue=progress_queue, task_id=task_id)
    return [
        {
            "rep": rep,
            "api": api,
            "model": model,
            "stage": stage,
            "test_name": func_name,
            "total": total,
            "soundness": soundness,
            "validity": validity,
            "mem_charged": mem_charged,
        }
        for func_name, total, soundness, validity, mem_charged in func_results
    ]


def _progress_display(queue, n_slots: int) -> None:
    # The ONLY thread that calls any tqdm method.
    # All terminal output — bar updates AND text messages — is serialised through this thread
    # via the queue, eliminating races between bar redraws and printed lines.
    #
    # n_slots bars are pre-created at fixed positions so they never shift.
    # Completed slots are freed and reused by the next incoming task.
    slot_bars = [
        tqdm(total=1, desc="", position=i, leave=True, dynamic_ncols=True, bar_format="{desc}")
        for i in range(n_slots)
    ]
    # task_to_slot maps the globally-unique task_id to its bar-slot index.
    # Because task_ids are unique, concurrent workers can never collide here.
    task_to_slot: dict[str, int] = {}
    free_slots = list(range(n_slots))

    while True:
        msg = queue.get()
        if msg is None:  # sentinel: shut down cleanly
            for bar in slot_bars:
                bar.close()
            break
        kind = msg[0]
        if kind == "start":
            _, task_id, total = msg
            if free_slots:
                slot = free_slots.pop(0)
                bar = slot_bars[slot]
                bar.bar_format = None  # restore default progress-bar format
                bar.reset(total=total)
                bar.set_description(task_id[-40:])  # show the tail: api/stage/rep
                task_to_slot[task_id] = slot
        elif kind == "update":
            _, task_id = msg
            if task_id in task_to_slot:
                slot_bars[task_to_slot[task_id]].update(1)
        elif kind == "done":
            _, task_id = msg
            if task_id in task_to_slot:
                slot = task_to_slot.pop(task_id)
                bar = slot_bars[slot]
                bar.bar_format = "{desc}"
                bar.set_description("")
                bar.refresh()
                free_slots.append(slot)
                free_slots.sort()
        elif kind == "write":
            # Text output routed here so it never races with bar redraws.
            tqdm.write(msg[1])


# Shared event: set = paused, cleared = running. Checked by the main loop between results.
_pause_event = threading.Event()


def _make_keyboard_listener(progress_queue):
    # Returns a closure that captures the queue, so pause messages are
    # also routed through the display thread instead of calling tqdm.write directly.
    def _listener():
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key == b"p":
                    if _pause_event.is_set():
                        _pause_event.clear()
                        progress_queue.put(("write", "Resumed."))
                    else:
                        _pause_event.set()
                        progress_queue.put(("write", "Paused. Press 'p' to resume."))
            time.sleep(0.05)
    return _listener


def collect_tests(model_filter: str | None = None):
    """Yield (model, api, stage, rep, path) for every test file under proptests/."""
    for model_dir in sorted(PROPTESTS_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        if model_filter and model_dir.name != model_filter:
            continue
        for api_dir in sorted(model_dir.iterdir()):
            if not api_dir.is_dir():
                continue
            for stage_dir in sorted(api_dir.iterdir()):
                if not stage_dir.is_dir():
                    continue
                for test_file in sorted(stage_dir.glob("pbt_*.py")):
                    rep = int(test_file.stem.split("_")[1])
                    yield model_dir.name, api_dir.name, stage_dir.name, rep, test_file


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Measure validity/soundness of the proptests corpus.",
    )
    parser.add_argument("model", nargs="?", default=None,
                        help="restrict to one model directory (default: all models)")
    parser.add_argument("--mem-cap-gb", type=float, default=DEFAULT_MEM_CAP_GB,
                        help="hard commit cap per worker in GiB (default: %(default)s)")
    parser.add_argument("--soft-frac", type=float, default=DEFAULT_SOFT_FRAC,
                        help="soft bail threshold as a fraction of the cap (default: %(default)s)")
    parser.add_argument("--maxtasksperchild", type=int, default=DEFAULT_MAXTASKSPERCHILD,
                        help="recycle each worker after this many files (default: %(default)s)")
    parser.add_argument("--workers", type=int, default=None,
                        help="worker count (default: auto from CPUs and available RAM)")
    parser.add_argument("--no-mem-cap", action="store_true",
                        help="disable all memory containment (pre-cap behavior)")
    return parser.parse_args()


def main():
    args = _parse_args()
    model_filter = args.model

    tests = list(collect_tests(model_filter))

    if not tests:
        available = [d.name for d in sorted(PROPTESTS_DIR.iterdir()) if d.is_dir()]
        print(f"No tests found. Available models: {available}")
        sys.exit(1)

    cap_bytes = None if args.no_mem_cap else int(args.mem_cap_gb * 2**30)

    if args.workers is not None:
        workers = args.workers
        workers_reason = "--workers"
    elif cap_bytes is None:
        workers = min(cpu_count() // 2, len(tests))
        workers_reason = "cpu_count()//2 (no memory cap)"
    else:
        # Bound workers so all of them at the cap simultaneously still fit in
        # ~80% of currently-available physical RAM (the cap is a limit, not a
        # reservation — override with --workers if this is too conservative).
        by_mem = max(1, int(_available_phys_bytes() * 0.8 // cap_bytes))
        workers = min(cpu_count() // 2, len(tests), by_mem)
        workers_reason = (
            f"min(cpu_count()//2={cpu_count() // 2}, RAM-bound={by_mem} "
            f"at {args.mem_cap_gb:g}GiB/worker)"
        )

    rows = []

    with Manager() as manager:
        progress_queue = manager.Queue()

        # Print startup messages before bars exist — safe to use print here.
        if model_filter:
            print(f"Filtering to model: {model_filter}")
        if cap_bytes is not None:
            print(f"Memory cap: {args.mem_cap_gb:g}GiB/worker "
                  f"(soft bail at {args.soft_frac:.0%}), recycling workers "
                  f"every {args.maxtasksperchild} files")
        print(f"Running {len(tests)} test files across {workers} workers ({workers_reason})...")
        print("Press 'p' at any time to pause/resume.\n")

        # Keyboard listener sends pause messages through the queue so they
        # are serialised with bar updates in the display thread.
        threading.Thread(target=_make_keyboard_listener(progress_queue), daemon=True).start()

        # Display thread is the sole owner of all tqdm state and all terminal writes.
        display_thread = threading.Thread(target=_progress_display, args=(progress_queue, workers), daemon=True)
        display_thread.start()

        test_args = [(m, a, s, r, p, progress_queue) for m, a, s, r, p in tests]

        with Pool(
            workers,
            initializer=_worker_init,
            initargs=(cap_bytes, args.soft_frac),
            maxtasksperchild=args.maxtasksperchild,
        ) as pool:
            for i, row_list in enumerate(pool.imap_unordered(_worker, test_args, chunksize=1), 1):
                while _pause_event.is_set():
                    time.sleep(0.5)
                if row_list:
                    r = row_list[0]
                    # Route through the queue so this never races with bar redraws.
                    progress_queue.put((
                        "write",
                        f"[{i}/{len(tests)}] {r['model']} / {r['api']} / {r['stage']} / rep {r['rep']}"
                        f" — {len(row_list)} function(s)",
                    ))
                rows.extend(row_list)

        progress_queue.put(None)  # signal display thread to exit
        display_thread.join(timeout=5)  # wait before Manager tears down the queue proxy

    rows.sort(key=lambda r: (r["rep"], r["stage"], r["api"], r["model"], r["test_name"]))

    fieldnames = [
        "rep", "api", "model", "stage", "test_name",
        "total", "soundness", "validity", "mem_charged",
    ]
    suffix = f"_{model_filter}" if model_filter else ""

    csv_path = Path(f"results{suffix}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved to {csv_path}")

    xlsx_path = Path(f"results{suffix}.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.append(fieldnames)
    for row in rows:
        ws.append([row[f] for f in fieldnames])
    wb.save(xlsx_path)
    print(f"XLSX saved to {xlsx_path}")


if __name__ == "__main__":
    main()
