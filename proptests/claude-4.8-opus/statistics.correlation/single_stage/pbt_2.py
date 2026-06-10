from hypothesis import given, strategies as st
import math
import statistics
import pytest

# Summary: Generate a bounded float list `x` (len >= 2), then derive `y` via one of
# several relationship "modes": perfect positive/negative linear, perfect monotonic
# nonlinear, arbitrary, or constant. Randomly pick the correlation method. Check
# the documented bounds [-1, 1], the perfect-correlation values for each mode, and
# that constant inputs (or invalid lengths) raise StatisticsError.
@given(st.data())
def test_statistics_correlation(data):
    floats = st.floats(allow_nan=False, allow_infinity=False,
                       min_value=-1e6, max_value=1e6)
    x = data.draw(st.lists(floats, min_size=2, max_size=30))

    mode = data.draw(st.sampled_from(
        ["pos_linear", "neg_linear", "monotonic", "arbitrary",
         "constant", "bad_length"]))
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    if mode == "pos_linear":
        a = data.draw(st.floats(min_value=1e-3, max_value=1e3))
        b = data.draw(floats)
        y = [a * v + b for v in x]
    elif mode == "neg_linear":
        a = data.draw(st.floats(min_value=1e-3, max_value=1e3))
        b = data.draw(floats)
        y = [-a * v + b for v in x]
    elif mode == "monotonic":
        # strictly increasing distinct positive values -> perfect Spearman
        n = len(x)
        x = [float(i + 1) for i in range(n)]
        y = [v ** 3 for v in x]
    elif mode == "arbitrary":
        y = data.draw(st.lists(floats, min_size=len(x), max_size=len(x)))
    elif mode == "constant":
        # make x constant -> must raise StatisticsError
        x = [data.draw(floats)] * len(x)
        y = data.draw(st.lists(floats, min_size=len(x), max_size=len(x)))
    else:  # bad_length
        y = data.draw(st.lists(floats, min_size=len(x) + 1, max_size=len(x) + 1))

    # Constant-input and bad-length cases must raise StatisticsError.
    if mode == "constant":
        if len(set(y)) <= 1:  # y could also be constant by chance; still error
            with pytest.raises(statistics.StatisticsError):
                statistics.correlation(x, y, method=method)
            return
        with pytest.raises(statistics.StatisticsError):
            statistics.correlation(x, y, method=method)
        return
    if mode == "bad_length":
        with pytest.raises(statistics.StatisticsError):
            statistics.correlation(x, y, method=method)
        return

    # Skip degenerate cases where derived y is effectively constant
    # (e.g. pos/neg linear with a*range collapsing or arbitrary constant).
    if len(set(x)) <= 1 or len(set(y)) <= 1:
        with pytest.raises(statistics.StatisticsError):
            statistics.correlation(x, y, method=method)
        return

    r = statistics.correlation(x, y, method=method)

    # Property 1: coefficient must lie within [-1, +1] (allow tiny float slack).
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9

    # Property 2: perfect relationships.
    if mode == "pos_linear" and method == "linear":
        assert math.isclose(r, 1.0, abs_tol=1e-6)
    elif mode == "neg_linear" and method == "linear":
        assert math.isclose(r, -1.0, abs_tol=1e-6)
    elif mode == "monotonic" and method == "ranked":
        assert math.isclose(r, 1.0, abs_tol=1e-6)
# End program