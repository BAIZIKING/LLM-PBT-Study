from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_slope_intercept_are_finite(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert math.isfinite(slope)
    assert math.isfinite(intercept)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_swapping_x_y_inverts_regression(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    swapped_slope, swapped_intercept = statistics.linear_regression(y, x)
    assert math.isclose(slope, 1 / swapped_slope, rel_tol=1e-9)
    assert math.isclose(intercept, -swapped_intercept / swapped_slope, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_linear_scaling_of_x_y(x, y, scale):
    slope, intercept = statistics.linear_regression(x, y)
    scaled_slope, scaled_intercept = statistics.linear_regression([i * scale for i in x], [i * scale for i in y])
    assert math.isclose(slope * scale, scaled_slope, rel_tol=1e-9)
    assert math.isclose(intercept, scaled_intercept, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.floats(allow_nan=False, allow_infinity=False))
def test_adding_constant_to_y(x, y, constant):
    slope, intercept = statistics.linear_regression(x, y)
    shifted_slope, shifted_intercept = statistics.linear_regression(x, [i + constant for i in y])
    assert math.isclose(slope, shifted_slope, rel_tol=1e-9)
    assert math.isclose(intercept + constant, shifted_intercept, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_proportional_intercept_is_zero(x, y):
    _, intercept = statistics.linear_regression(x, y, proportional=True)
    assert math.isclose(intercept, 0.0, rel_tol=1e-9)
# End program