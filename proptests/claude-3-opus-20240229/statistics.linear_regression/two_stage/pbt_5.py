from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_linear_regression_finite_output(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert math.isfinite(slope) and math.isfinite(intercept)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_linear_regression_swap_input(x, y):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression(y, x)
    assert math.isclose(slope1, 1/slope2, rel_tol=1e-9) and math.isclose(intercept1, -intercept2/slope2, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_linear_regression_scale_input(x, y, scale):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([xi * scale for xi in x], [yi * scale for yi in y])
    assert math.isclose(slope1 * scale, slope2, rel_tol=1e-9) and math.isclose(intercept1, intercept2, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_linear_regression_shift_input(x, y, shift):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([xi + shift for xi in x], y)
    assert math.isclose(slope1, slope2, rel_tol=1e-9) and math.isclose(intercept1, intercept2 + slope1 * shift, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_linear_regression_proportional(x, y):
    _, intercept1 = statistics.linear_regression(x, y, proportional=True)
    slope, intercept2 = statistics.linear_regression(x, y, proportional=False)
    assert math.isclose(intercept1, 0.0, abs_tol=1e-9)
    assert math.isclose(intercept2, statistics.mean(y) - slope * statistics.mean(x), rel_tol=1e-9)
# End program