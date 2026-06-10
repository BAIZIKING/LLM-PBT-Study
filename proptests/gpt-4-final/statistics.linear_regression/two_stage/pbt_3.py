from hypothesis import given, strategies as st
import statistics
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_linear_regression_length(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert len([slope, intercept]) == 2

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_linear_regression_output_types(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    assert isinstance(slope, float)
    assert isinstance(intercept, float)
    
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_linear_regression_dependent_on_inputs(x, y):
    slope, intercept = statistics.linear_regression(x, y)
    std_x = np.std(x)
    std_y = np.std(y)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    assert np.isclose(slope, std_y / std_x)
    assert np.isclose(intercept, mean_y - slope * mean_x)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_linear_regression_proportional(x, y):
    slope, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0

@given(st.lists(st.just(1.0), min_size=2),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_linear_regression_value_x(x, y):
    try:
        statistics.linear_regression(x, y)
    except StatisticsError:
        assert True
    else:
        assert False