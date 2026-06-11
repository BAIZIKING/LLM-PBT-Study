"""
This is the same as validity_soundness_windows but with keyboard detection
(msvcrt pause/resume) and worker memory limitation (ctypes Job Object cap)
removed, so it runs on Linux. The input-generation error handling — strategy
crash sentinels and the engine-restart retry loop — is retained and is platform
independent.
"""

import contextlib
import csv
import functools
import sys
import threading
import warnings
from multiprocessing import Manager, Pool, cpu_count
from pathlib import Path

from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st
from hypothesis.errors import StopTest, Unsatisfiable
from hypothesis.reporting import with_reporter
from hypothesis.strategies import SearchStrategy
from openpyxl import Workbook
from tqdm import tqdm

PROPTESTS_DIR = Path(__file__).parent / "proptests"
TOTAL_RUNS = 1000


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
        except BaseException:
            # Consume fresh entropy: a strategy that crashes before drawing any
            # choices (including MemoryError on an oversized allocation) would
            # otherwise produce the same empty choice sequence every time, and
            # the engine would stop after one example thinking the search space
            # is exhausted.
            draw(st.integers(min_value=0, max_value=2**64))
            return _GEN_CRASH
    return _safe()


def _make_counting_runner(func):
    """
    Extract the @given strategies from func's closure, re-apply them to a non-raising
    wrapper, and return (counting_wrapped, executed, assertion_errors, other_errors)
    where all but the first are single-element counter lists.

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

    @functools.wraps(inner)
    def counting_inner(*args, **kwargs):
        executed[0] += 1
        gen_values = list(args) + list(kwargs.values())
        if any(v is _GEN_CRASH for v in gen_values):
            # Input generation crashed for this example: the input is invalid,
            # and the test body can't meaningfully run without it.
            other_errors[0] += 1
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
        except MemoryError:
            print("Memory Error")
        except BaseException:
            # SystemExit, GeneratorExit, BaseExceptionGroup, etc. — count and continue
            # rather than letting them escape to Hypothesis (which would print a
            # reproduction/seed message) or crash the worker process.
            other_errors[0] += 1

    counting_wrapped = given(**given_kwargs)(counting_inner)
    return counting_wrapped, executed, assertion_errors, other_errors


def run_test_file(
    test_path: Path, n: int = TOTAL_RUNS, progress_queue=None, task_id: str | None = None
) -> list[tuple[str, int, int, int]]:
    """Return a list of (test_name, total, soundness, validity) — one entry per test function.

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

        try:
            exec(compile(source, str(test_path), "exec"), namespace)
        except Exception:
            return [("<load_error>", n, n, 0)]

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
                counting_wrapped, executed, ae_list, oe_list = runner_info
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
            else:
                print("wrapping failed for test at",  str(test_path))
                # Fallback for non-@given or unrecognised decorator shapes.
                assertion_errors = 0
                other_errors = 0
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
                    except Exception:
                        other_errors += 1

            if progress_queue is not None:
                progress_queue.put(("update", key))

            soundness = n - assertion_errors
            validity = n - other_errors
            results.append((func_name, n, soundness, validity))

        if progress_queue is not None:
            progress_queue.put(("done", key))

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
        }
        for func_name, total, soundness, validity in func_results
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


def main():
    model_filter = sys.argv[1] if len(sys.argv) == 2 else None

    tests = list(collect_tests(model_filter))

    if not tests:
        available = [d.name for d in sorted(PROPTESTS_DIR.iterdir()) if d.is_dir()]
        print(f"No tests found. Available models: {available}")
        sys.exit(1)

    workers = min(1, len(tests)) # maybe it is better this way

    rows = []

    with Manager() as manager:
        progress_queue = manager.Queue()

        # Print startup messages before bars exist — safe to use print here.
        if model_filter:
            print(f"Filtering to model: {model_filter}")
        print(f"Running {len(tests)} test files across {workers} workers...")

        # Display thread is the sole owner of all tqdm state and all terminal writes.
        display_thread = threading.Thread(target=_progress_display, args=(progress_queue, workers), daemon=True)
        display_thread.start()

        test_args = [(m, a, s, r, p, progress_queue) for m, a, s, r, p in tests]

        with Pool(workers) as pool:
            for i, row_list in enumerate(pool.imap_unordered(_worker, test_args), 1):
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

    fieldnames = ["rep", "api", "model", "stage", "test_name", "total", "soundness", "validity"]
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
    if len(sys.argv) > 2:
        print("Usage: python validity_soundness.py [<model_name>]")
        print("  No argument: run all models")
        print("  With argument: python validity_soundness.py gpt-4-final")
        sys.exit(1)
    main()
