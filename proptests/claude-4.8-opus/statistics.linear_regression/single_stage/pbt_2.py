from hypothesis import given, strategies as st, assume
import statistics
import math

# Summary: Generate equal-length lists of finite floats with a non-constant x.
# Build y exactly from a known slope/intercept to test parameter recovery and
# the proportional=False/True contracts. Separately test error conditions
# (unequal length, length < 2, constant x). Verify return type, intercept==0
# in proportional mode, and recovery of regression parameters.
@given(st.data())
def test_statistics_linear_regression(data):
    finite = st.floats(allow_nan=False, allow_infinity=False,
                       min_value=-1e6, max_value=1e6)

    # --- Error case 1: length < 2 ---
    short_x = data.draw(st.lists(finite, min_size=0, max_size=1))
    short_y = [0.0] * len(short_x)
    try:
        statistics.linear_regression(short_x, short_y)
        assert False, "Expected StatisticsError for length < 2"
    except statistics.StatisticsError:
        pass

    # --- Error case 2: unequal length ---
    n = data.draw(st.integers(min_value=2, max_value=20))
    ux = data.draw(st.lists(finite, min_size=n, max_size=n))
    uy = data.draw(st.lists(finite, min_size=n + 1, max_size=n + 1))
    try:
        statistics.linear_regression(ux, uy)
        assert False, "Expected StatisticsError for unequal lengths"
    except statistics.StatisticsError:
        pass

    # --- Error case 3: constant x ---
    const_val = data.draw(finite)
    const_x = [const_val] * n
    cy = data.draw(st.lists(finite, min_size=n, max_size=n))
    try:
        statistics.linear_regression(const_x, cy)
        assert False, "Expected StatisticsError for constant x"
    except statistics.StatisticsError:
        pass

    # --- Valid case: build y from a known slope/intercept ---
    x = data.draw(st.lists(finite, min_size=2, max_size=30, unique=True))
    n = len(x)
    # Need at least 2 points and non-constant x; unique=True guarantees both.
    true_slope = data.draw(finite)
    true_intercept = data.draw(finite)
    y = [true_slope * xi + true_intercept for xi in x]

    # Non-proportional regression
    result = statistics.linear_regression(x, y)
    slope, intercept = result
    assert hasattr(result, "slope") and hasattr(result, "intercept")
    assert isinstance(slope, float) and isinstance(intercept, float)

    # Recovery of parameters (data lies exactly on a line)
    scale = max(1.0, abs(true_slope), abs(true_intercept))
    assert math.isclose(slope, true_slope, rel_tol=1e-6, abs_tol=1e-6 * scale)
    assert math.isclose(intercept, true_intercept,
                        rel_tol=1e-6, abs_tol=1e-6 * scale)

    # Predicted values should match actual y (fit reproduces the line)
    for xi, yi in zip(x, y):
        pred = slope * xi + intercept
        assert math.isclose(pred, yi, rel_tol=1e-6,
                            abs_tol=1e-6 * max(1.0, abs(yi)))

    # --- Proportional mode: intercept must always be exactly 0.0 ---
    prop_result = statistics.linear_regression(x, y, proportional=True)
    assert prop_result.intercept == 0.0
# End program