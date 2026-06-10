from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_slope_intercept_are_floats(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert isinstance(slope, float)
    assert isinstance(intercept, float)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_swapped_input_lists(x, y):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression(y, x)
    assert math.isclose(slope1, 1 / slope2)
    assert math.isclose(intercept1, intercept2 / slope2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_linearly_scaled_input(x, y, scale):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([i * scale for i in x], [i * scale for i in y])
    assert math.isclose(slope1 * scale, slope2)
    assert math.isclose(intercept1, intercept2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_constant_added_to_x(x, y, constant):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([i + constant for i in x], y)
    assert math.isclose(slope1, slope2)
    assert math.isclose(intercept1 + slope1 * constant, intercept2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=0.0), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=0.0), min_size=2))
def test_proportional_input(x, y):
    slope, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0
    assert math.isclose(slope, statistics.mean(y) / statistics.mean(x))
# End program