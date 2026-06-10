from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of floats, avoiding very large values to prevent overflows.
float_list_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6), min_size=2)

@given(x=float_list_strategy, y=float_list_strategy)
def test_output_type(x, y):
    """Test that the function always returns a tuple of two floats."""
    slope, intercept = statistics.linear_regression(x, y)
    assert isinstance(slope, float) and isinstance(intercept, float)

@given(x=float_list_strategy, y=float_list_strategy)
def test_order_invariance(x, y):
    """Test that the order of elements in x and y does not affect the result."""
    result1 = statistics.linear_regression(x, y)
    result2 = statistics.linear_regression(list(reversed(x)), list(reversed(y)))
    assert result1 == result2

@given(x=float_list_strategy, y=float_list_strategy, shift=st.floats(allow_nan=False, allow_infinity=False))
def test_shift_invariance(x, y, shift):
    """Test that shifting x and y by a constant does not change the slope."""
    shifted_x = [xi + shift for xi in x]
    shifted_y = [yi + shift for yi in y]
    slope1, _ = statistics.linear_regression(x, y)
    slope2, _ = statistics.linear_regression(shifted_x, shifted_y)
    assert slope1 == slope2

@given(x=float_list_strategy, y=float_list_strategy, scale=st.floats(allow_nan=False, allow_infinity=False, min_value=1e-6, max_value=1e6)) # Avoid scale of 0
def test_scale_invariance(x, y, scale):
    """Test that scaling x and y by a constant does not change the slope."""
    scaled_x = [xi * scale for xi in x]
    scaled_y = [yi * scale for yi in y]
    slope1, _ = statistics.linear_regression(x, y)
    slope2, _ = statistics.linear_regression(scaled_x, scaled_y)
    assert slope1 == slope2

@given(x=float_list_strategy, y=float_list_strategy)
def test_proportional_mode(x, y):
    """Test that the intercept is always 0.0 when proportional=True."""
    _, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0
# End program