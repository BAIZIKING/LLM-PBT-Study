from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_returned_values_are_finite(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert math.isfinite(slope)
    assert math.isfinite(intercept)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_swapping_input_arrays(x, y):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression(y, x)
    assert math.isclose(slope1, 1/slope2)
    assert math.isclose(intercept1, intercept2/slope2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_adding_constant_to_y(x, y, c):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression(x, [yi + c for yi in y])
    assert math.isclose(slope1, slope2)
    assert math.isclose(intercept2, intercept1 + c*slope1)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False, min_value=0))
def test_multiplying_x_by_constant(x, y, c):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([xi * c for xi in x], y)
    assert math.isclose(slope1*c, slope2)
    assert math.isclose(intercept1, intercept2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_proportional_flag(x, y):
    _, intercept1 = statistics.linear_regression(x, y, proportional=True)
    _, intercept2 = statistics.linear_regression(x, y, proportional=False)
    assert intercept1 == 0.0
    # intercept2 may or may not be 0.0 depending on the input
# End program