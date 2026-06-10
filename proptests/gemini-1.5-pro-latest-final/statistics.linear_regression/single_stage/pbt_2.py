from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a wide variety of inputs for the statistics.linear_regression function, including edge cases. 
# It generates two lists of floats (x and y) with varying lengths and values. 
# The strategy also includes cases where x is constant to test the StatisticsError handling.

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate lists of floats with varying lengths and values
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=len(x)))

    # Include edge case: x is constant
    if data.draw(st.booleans()):
        x = [x[0]] * len(x)

    # Check if StatisticsError is raised when x is constant
    if x.count(x[0]) == len(x):
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(x, y)
    else:
        # Check if the function returns a tuple of two floats
        result = statistics.linear_regression(x, y)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

# End program