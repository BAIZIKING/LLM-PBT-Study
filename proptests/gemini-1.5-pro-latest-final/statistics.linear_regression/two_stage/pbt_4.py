from hypothesis import given, strategies as st
import statistics

# Define strategies for generating valid input data
# Restricting floats to avoid potential overflow issues
max_float = 1e5  # Adjust this value based on desired range
floats = st.floats(min_value=-max_float, max_value=max_float)

@given(st.data())
def test_linear_regression_output_type(data):
    x = data.draw(st.lists(floats, min_size=2))
    y = data.draw(st.lists(floats, min_size=2, max_size=len(x)))
    result = statistics.linear_regression(x, y)
    assert isinstance(result, tuple) and len(result) == 2
    assert all(isinstance(val, float) for val in result)

@given(st.data())
def test_linear_regression_order_invariance(data):
    data_list = data.draw(st.lists(floats, min_size=2))
    x = data_list[:]
    y = data_list[:]
    data.shuffle(x)
    data.shuffle(y)
    result1 = statistics.linear_regression(x, y)
    result2 = statistics.linear_regression(data_list, data_list)
    assert result1 == result2

@given(st.data())
def test_linear_regression_length_invariance(data):
    base_data = data.draw(st.lists(floats, min_size=2))
    extra_points = data.draw(st.lists(floats, min_size=1))
    x1 = base_data + extra_points
    y1 = base_data + extra_points
    result1 = statistics.linear_regression(x1, y1)
    result2 = statistics.linear_regression(base_data, base_data)
    assert result1 == result2 

@given(st.data())
def test_linear_regression_proportional_intercept(data):
    x = data.draw(st.lists(floats, min_size=2))
    y = data.draw(st.lists(floats, min_size=2, max_size=len(x)))
    slope, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0

@given(st.data())
def test_linear_regression_data_range_sensitivity(data):
    x = data.draw(st.lists(floats, min_size=2))
    y = data.draw(st.lists(floats, min_size=2, max_size=len(x)))
    scale_factor = data.draw(st.floats(min_value=0.1, max_value=10))  # Avoid scaling by zero
    x_scaled = [val * scale_factor for val in x]
    y_scaled = [val * scale_factor for val in y]
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression(x_scaled, y_scaled)
    assert slope1 == slope2
    assert intercept2 == intercept1 * scale_factor
# End program