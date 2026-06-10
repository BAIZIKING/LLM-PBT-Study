from hypothesis import given, strategies as st
import math
import statistics
from statistics import StatisticsError

# Summary: Generate two equal-length lists (length >= 2) of bounded, finite floats,
# choosing a random method ('linear' or 'ranked'). Check that valid inputs yield
# a coefficient in [-1, 1], that constant inputs raise StatisticsError, that the
# function is symmetric, and that a non-constant list correlated with itself gives 1.0.
@given(st.data())
def test_statistics_correlation(data):
    method = data.draw(st.sampled_from(['linear', 'ranked']))
    n = data.draw(st.integers(min_value=2, max_value=50))
    finite_floats = st.floats(
        allow_nan=False, allow_infinity=False,
        min_value=-1e6, max_value=1e6, width=64,
    )
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))

    x_constant = len(set(x)) <= 1
    y_constant = len(set(y)) <= 1

    if x_constant or y_constant:
        # Property: constant input must raise StatisticsError
        try:
            statistics.correlation(x, y, method=method)
            assert False, "Expected StatisticsError for constant input"
        except StatisticsError:
            pass
        return

    # Property 1: result is bounded in [-1, 1] (allow small float tolerance)
    r = statistics.correlation(x, y, method=method)
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9

    # Property 2: symmetry
    r_swapped = statistics.correlation(y, x, method=method)
    assert math.isclose(r, r_swapped, rel_tol=1e-9, abs_tol=1e-9)

    # Property 3: perfect self-correlation equals 1.0 for non-constant data
    r_self = statistics.correlation(x, x, method=method)
    assert math.isclose(r_self, 1.0, rel_tol=1e-9, abs_tol=1e-9)
# End program