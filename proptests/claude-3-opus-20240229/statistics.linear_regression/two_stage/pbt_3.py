from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_linear_regression_output_validity(x, y):
    try:
        slope, intercept = statistics.linear_regression(x, y)
        assert isinstance(slope, float) and math.isfinite(slope)
        assert isinstance(intercept, float) and math.isfinite(intercept)
    except statistics.StatisticsError:
        assert len(x) != len(y) or len(x) < 2 or len(set(x)) == 1

@given(st.lists(st.floats(min_value=0, max_value=1e6), min_size=2), 
       st.lists(st.floats(min_value=0, max_value=1e6), min_size=2))
def test_linear_regression_slope_direction(x, y):
    try:
        slope, _ = statistics.linear_regression(x, y)
        correlation = statistics.correlation(x, y)
        if correlation > 0.9:
            assert slope > 0
        elif correlation < -0.9:
            assert slope < 0
    except statistics.StatisticsError:
        assert len(x) != len(y) or len(x) < 2 or len(set(x)) == 1

@given(st.lists(st.floats(min_value=0, max_value=1e6), min_size=2))
def test_linear_regression_proportional(x):
    try:
        _, intercept = statistics.linear_regression(x, [y * 2 for y in x], proportional=True)
        assert intercept == 0.0
    except statistics.StatisticsError:
        assert len(x) < 2 or len(set(x)) == 1

@given(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=2),
       st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=2))
def test_linear_regression_predicted_actual_correlation(x, y):
    try:
        slope, intercept = statistics.linear_regression(x, y)
        y_pred = [slope * xi + intercept for xi in x]
        correlation = statistics.correlation(y_pred, y)
        assert correlation > 0.9
    except statistics.StatisticsError:
        assert len(x) != len(y) or len(x) < 2 or len(set(x)) == 1

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=1), 
       st.lists(st.floats(allow_nan=False, allow_infinity=False)),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_linear_regression_input_validation(x, y, z):
    try:
        statistics.linear_regression(x, y)
        assert False, "Expected StatisticsError for input with length less than 2"
    except statistics.StatisticsError:
        pass
    
    try:
        statistics.linear_regression(y, z)
        assert False, "Expected StatisticsError for input with unequal lengths"
    except statistics.StatisticsError:
        pass
    
    try:
        statistics.linear_regression([1.0] * 5, y)
        assert False, "Expected StatisticsError for constant input"
    except statistics.StatisticsError:
        pass
# End program