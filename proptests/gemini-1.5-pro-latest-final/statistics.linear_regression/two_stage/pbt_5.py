from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of floats avoiding very large values
safe_floats = st.floats(allow_nan=False, allow_infinity=False, width=32)

@given(st.data())
def test_linear_regression_output_type(data):
    # Generate lists of floats for x and y
    x = data.draw(st.lists(safe_floats, min_size=2))
    y = data.draw(st.lists(safe_floats, min_size=2, min_size=len(x)))
    # Ensure x is not constant to avoid StatisticsError
    assume(len(set(x)) > 1)
    # Test that the output is a tuple of two floats
    result = statistics.linear_regression(x, y)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(val, float) for val in result)

@given(st.data())
def test_linear_regression_slope_sign(data):
    # Generate lists of floats
    x = data.draw(st.lists(safe_floats, min_size=2))
    y = data.draw(st.lists(safe_floats, min_size=2, min_size=len(x)))
    # Ensure x is not constant to avoid StatisticsError
    assume(len(set(x)) > 1)
    # Calculate correlation and slope
    correlation = statistics.correlation(x, y)
    slope, _ = statistics.linear_regression(x, y)
    # Test that the sign of the slope matches the correlation
    if correlation > 0:
        assert slope > 0
    elif correlation < 0:
        assert slope < 0

@given(st.data())
def test_linear_regression_proportional(data):
    # Generate lists of floats
    x = data.draw(st.lists(safe_floats, min_size=2))
    y = data.draw(st.lists(safe_floats, min_size=2, min_size=len(x)))
    # Ensure x is not constant to avoid StatisticsError
    assume(len(set(x)) > 1)
    # Test that the intercept is 0.0 when proportional is True
    _, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0

@given(st.data())
def test_linear_regression_data_order(data):
    # Generate lists of floats
    x = data.draw(st.lists(safe_floats, min_size=2, unique=True))  # Ensure unique values to avoid sorting issues
    y = data.draw(st.lists(safe_floats, min_size=2, min_size=len(x)))
    # Calculate regression with original order
    slope1, intercept1 = statistics.linear_regression(x, y)
    # Calculate regression with reversed order
    slope2, intercept2 = statistics.linear_regression(list(reversed(x)), list(reversed(y)))
    # Test that the results are the same
    assert slope1 == slope2
    assert intercept1 == intercept2 

@given(st.data())
def test_linear_regression_shift_invariance(data):
    # Generate lists of floats
    x = data.draw(st.lists(safe_floats, min_size=2))
    y = data.draw(st.lists(safe_floats, min_size=2, min_size=len(x)))
    # Ensure x is not constant to avoid StatisticsError
    assume(len(set(x)) > 1)
    # Generate a random shift value
    shift = data.draw(safe_floats)
    # Calculate regression with original data
    slope1, _ = statistics.linear_regression(x, y)
    # Calculate regression with shifted data
    slope2, _ = statistics.linear_regression([val + shift for val in x], y)
    # Test that the slopes are the same
    assert slope1 == slope2 
# End program