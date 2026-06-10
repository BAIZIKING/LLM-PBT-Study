from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2).filter(lambda x: len(set(x)) > 1), 
       st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2))
def test_linear_regression_length_and_content(x, y):
    assert len(x) == len(y), "Lengths of x and y must be the same"
    slope, intercept = statistics.linear_regression(x, y)
    assert isinstance(slope, float), "Slope must be float"
    assert isinstance(intercept, float), "Intercept must be float"

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), 
       st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), 
       st.booleans())
def test_linear_regression_proportional(x, y, proportional):
    if len(set(x)) > 1 and len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y, proportional=proportional)
        if proportional:
            assert math.isclose(intercept, 0, abs_tol=1e-3), "When proportional is True, Intercept must be 0"

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2).filter(lambda x: len(set(x)) > 1), 
       st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2))
def test_linear_regression_output(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y)
        y_predicted = [slope*value + intercept for value in x]
        assert statistics.correlation(x, y_predicted) >= 0.9, "Predicted and actual y values correlation must be high"
        
# End program