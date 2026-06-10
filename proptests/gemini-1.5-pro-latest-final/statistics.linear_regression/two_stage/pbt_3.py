from hypothesis import given, strategies as st
import statistics

# Property 1: Output Type
@given(st.lists(st.floats(allow_nan=False), min_size=2), st.lists(st.floats(allow_nan=False), min_size=2))
def test_linear_regression_output_type(x, y):
    result = statistics.linear_regression(x, y)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(val, float) for val in result)

# Property 2: Order Invariance 
@given(st.lists(st.floats(allow_nan=False), min_size=2), st.lists(st.floats(allow_nan=False), min_size=2))
def test_linear_regression_order_invariance(x, y):
    result1 = statistics.linear_regression(x, y)
    result2 = statistics.linear_regression(list(reversed(x)), list(reversed(y)))
    assert result1 == result2

# Property 3: Proportional Regression Slope
@given(st.lists(st.floats(min_value=0.001, allow_nan=False), min_size=2), st.lists(st.floats(min_value=0.001, allow_nan=False), min_size=2))
def test_linear_regression_proportional_slope(x, y):
    result = statistics.linear_regression(x, y, proportional=True)
    assert result[1] == 0.0  # Intercept should be 0
    if all(a * b > 0 for a, b in zip(x, y)):  # Same sign
        assert result[0] > 0
    else:
        assert result[0] < 0

# Property 4: Data Range Influence 
@given(st.lists(st.floats(allow_nan=False), min_size=2), st.lists(st.floats(allow_nan=False), min_size=2), st.floats(min_value=0.001, allow_nan=False))
def test_linear_regression_scaling(x, y, factor):
    result1 = statistics.linear_regression(x, y)
    scaled_x = [i * factor for i in x]
    scaled_y = [i * factor for i in y]
    result2 = statistics.linear_regression(scaled_x, scaled_y)
    assert result1[0] == result2[0]  # Slope remains same
    assert result1[1] * factor == result2[1]  # Intercept scales with factor

# Property 5: Shift Invariance
@given(st.lists(st.floats(allow_nan=False), min_size=2), st.lists(st.floats(allow_nan=False), min_size=2), st.floats(allow_nan=False))
def test_linear_regression_shift(x, y, shift):
    result1 = statistics.linear_regression(x, y)
    shifted_x = [i + shift for i in x]
    shifted_y = [i + shift for i in y]
    result2 = statistics.linear_regression(shifted_x, shifted_y)
    assert result1[0] == result2[0]  # Slope remains same
    assert result1[1] + shift == result2[1]  # Intercept reflects the shift

# End program