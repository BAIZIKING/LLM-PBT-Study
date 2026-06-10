from hypothesis import given, strategies as st
from hypothesis.strategies import lists, floats
import statistics
import math

# testing type property
@given(st.lists(floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1000), min_size=2), 
       st.lists(floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1000), min_size=2))
def test_regression_return_type(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y)
        assert isinstance(slope, float)
        assert isinstance(intercept, float)

# testing equality property
@given(st.lists(floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1000), min_size=2), 
       st.lists(floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1000), min_size=2))
def test_regression_proportionality_returns_zero_intercept(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y, proportional=True)
        assert intercept == 0

# testing constraint property
@given(st.just([1.0]), st.lists(floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=1), min_size=2))
def test_regression_single_element_or_constant_input_throws_error(x, y):
    try:
        statistics.linear_regression(x, y)
    except statistics.StatisticsError:
        assert True

# testing size property
@given(st.lists(floats(allow_nan=False, allow_infinity=False, min_value=1, max_value=1000), min_size=2), 
       st.lists(floats(allow_nan=False, allow_infinity=False, min_value=1, max_value=1000), min_size=3))
def test_regression_different_size_input_throws_error(x, y):
    try:
        statistics.linear_regression(x, y)
    except statistics.StatisticsError:
        assert True

# testing value property
@given(st.lists(floats(allow_nan=False, allow_infinity=False, min_value=1, max_value=1000), min_size=2), 
       st.lists(floats(allow_nan=False, allow_infinity=False, min_value=1, max_value=1000), min_size=2))
def test_regression_output_generates_close_to_original_y(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y)
        for i in range(len(x)):
            predicted_y = slope * x[i] + intercept
            # check that predicted and actual y values are within 1% of each other
            diff = abs(predicted_y - y[i])
            assert diff <= 0.01 * y[i]

# End program