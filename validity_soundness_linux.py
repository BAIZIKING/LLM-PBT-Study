"""
This is the same as validity_soundness_windows but with tqdm, keyboard detection and worker memory limitation removed by AI
"""

import contextlib
import csv
import functools
import sys
import warnings
from multiprocessing import Pool, cpu_count
from pathlib import Path

from hypothesis import HealthCheck, Phase, assume, given, settings
from hypothesis.reporting import with_reporter
from openpyxl import Workbook

PROPTESTS_DIR = Path(__file__).parent / "proptests"
TOTAL_RUNS = 1000


class _DevNull:
    def write(self, *a): pass
    def flush(self): pass


def _make_counting_runner(func, n):
    """
    Extract the @given strategies from func's closure, re-apply them to a non-raising
    wrapper, and return (counting_wrapped, assertion_errors_list, other_errors_list).

    counting_wrapped() runs exactly n diverse Hypothesis examples. Because the inner
    wrapper never raises, Hypothesis never "finds" a failure and always runs all n
    examples — giving full coverage-guided exploration instead of n independent draws
    from the biased-toward-small geometric distribution.

    Returns None if the strategies cannot be extracted (fallback to original loop).
    """
    if not getattr(func, 'is_hypothesis_test', False):
        return None

    inner = func.hypothesis.inner_test
    given_kwargs = func.hypothesis._given_kwargs

    assertion_errors = [0]
    other_errors = [0]

    @functools.wraps(inner)
    def counting_inner(*args, **kwargs):
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
        except KeyboardInterrupt:
            raise
        except BaseException:
            # SystemExit, GeneratorExit, BaseExceptionGroup, etc. — count and continue
            # rather than letting them escape to Hypothesis (which would print a
            # reproduction/seed message) or crash the worker process.
            other_errors[0] += 1

    counting_wrapped = given(**given_kwargs)(counting_inner)
    counting_wrapped._hypothesis_internal_use_settings = settings(
        max_examples=n,
        deadline=None,  # counting_inner can't surface DeadlineExceeded; the engine
                         # raises it itself after the call, aborting the run early
                         # and printing a seed message — disable it entirely.
        suppress_health_check=list(HealthCheck),
        database=None,
        phases=[Phase.generate],
    )
    return counting_wrapped, assertion_errors, other_errors


def run_test_file(test_path: Path, n: int = TOTAL_RUNS) -> list[tuple[str, int, int, int]]:
    """Return a list of (test_name, total, soundness, validity) — one entry per test function."""
    source = test_path.read_text(encoding="utf-8")
    namespace = {"__name__": "__main__"}

    _out = _DevNull()
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

        results = []
        for func_name, func in test_funcs:
            runner_info = _make_counting_runner(func, n)

            if runner_info is not None:
                counting_wrapped, ae_list, oe_list = runner_info
                try:
                    counting_wrapped()
                except KeyboardInterrupt:
                    raise
                except BaseException:
                    # Any remaining engine-level exception (e.g. Flaky,
                    # InvalidArgument) — counting_inner already recorded what it
                    # could; just don't let it crash the worker.
                    pass
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

            soundness = n - assertion_errors
            validity = n - other_errors
            results.append((func_name, n, soundness, validity))

    return results


def _worker(args) -> list[dict]:
    model, api, stage, rep, test_path = args
    func_results = run_test_file(test_path)
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

    workers = min(cpu_count() // 2, len(tests))

    rows = []

    if model_filter:
        print(f"Filtering to model: {model_filter}")
    print(f"Running {len(tests)} test files across {workers} workers...\n")

    with Pool(workers) as pool:
        for i, row_list in enumerate(pool.imap_unordered(_worker, tests, chunksize=1), 1):
            if row_list:
                r = row_list[0]
                print(
                    f"[{i}/{len(tests)}] {r['model']} / {r['api']} / {r['stage']} / rep {r['rep']}"
                    f" — {len(row_list)} function(s)"
                )
            rows.extend(row_list)

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
