from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a wide variety of inputs for the linear_regression function, including edge cases, to thoroughly test its behavior.

# 1. Data Generation:
#   - lengths: We generate lists of varying lengths, including empty lists, lists with one element, and longer lists to test different input sizes.
#   - x_values: For the independent variable x, we generate lists of floats, ensuring they are not constant (all elements are the same) to avoid StatisticsError. 
#   - y_values: The dependent variable y is generated as a list of floats with the same length as x.

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate list lengths, ensuring they are at least 2 to avoid errors.
    list_length = data.draw(st.integers(min_value=2, max_value=100))

    # Generate x values as floats, ensuring they are not all the same.
    x_values = data.draw(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=list_length, unique=True)
    )

    # Generate y values as floats with the same length as x.
    y_values = data.draw(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=list_length, max_size=list_length)
    )

    # 2. Property Checking:
    #   - Output Type: Check if the function returns a tuple of two floats (slope and intercept).
    #   - StatisticsError: Test if a StatisticsError is raised when x is constant. 
    #   - Proportional Case: When proportional=True, ensure the intercept is approximately 0.0.

    # Check if the output is a tuple of two floats.
    result = statistics.linear_regression(x_values, y_values)
    assert isinstance(result, tuple) and len(result) == 2
    assert isinstance(result[0], float) and isinstance(result[1], float)

    # Test for StatisticsError when x is constant.
    constant_x = [x_values[0]] * list_length
    with pytest.raises(statistics.StatisticsError):
        statistics.linear_regression(constant_x, y_values)

    # Check if intercept is approximately 0.0 when proportional=True.
    proportional_result = statistics.linear_regression(x_values, y_values, proportional=True)
    assert math.isclose(proportional_result[1], 0.0, abs_tol=1e-10)

# End program