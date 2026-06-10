from hypothesis import given, assume, strategies as st
import math
import statistics

# Summary: Generate a length n >= 2, then build two equal-length lists of finite,
# bounded numbers. Ensure both lists are non-constant (>=2 distinct values) so the
# valid (non-error) code path is exercised. Randomly pick method in {'linear','ranked'}.
# Check that the result is in [-1, 1], is symmetric in its arguments, and that
# self-correlation equals 1.0.
@given(st.data())
def test_statistics_correlation(data):
    n = data.draw(st.integers(min_value=2, max_value=50))

    number = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(min_value=-1e6, max_value=1e6,
                  allow_nan=False, allow_infinity=False),
    )

    x = data.draw(st.lists(number, min_size=n, max_size=n))
    y = data.draw(st.lists(number, min_size=n, max_size=n))
    method = data.draw(st.sampled_from(['linear', 'ranked']))

    # Inputs must be non-constant, otherwise StatisticsError is raised.
    assume(len(set(x)) >= 2)
    assume(len(set(y)) >= 2)

    tol = 1e-9

    r = statistics.correlation(x, y, method=method)

    # Property 1: result is bounded in [-1, 1]
    assert -1.0 - tol <= r <= 1.0 + tol

    # Property 2: symmetry
    r_swapped = statistics.correlation(y, x, method=method)
    assert math.isclose(r, r_swapped, rel_tol=1e-9, abs_tol=1e-9)

    # Property 3: perfect self-correlation equals 1.0
    r_self = statistics.correlation(x, x, method=method)
    assert math.isclose(r_self, 1.0, rel_tol=1e-9, abs_tol=1e-9)
# End program