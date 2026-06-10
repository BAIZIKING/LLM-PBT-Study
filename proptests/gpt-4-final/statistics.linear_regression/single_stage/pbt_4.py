from hypothesis import given, strategies as st
import statistics

@given(
    x=st.lists(st.floats(min_value=-1e10, max_value=1e10), min_size=2), 
    y=st.lists(st.floats(min_value=-1e10, max_value=1e10), min_size=2),
    proportional=st.booleans()
)
def test_statistics_linear_regression(x, y, proportional):
    if len(x) != len(y): 
        return # x and y should have the same length, skip if they're not

    result = statistics.linear_regression(x, y, proportional=proportional)
    
    assert isinstance(result, tuple) # check the result is a tuple 
    assert len(result) == 2 # there should be 2 items in the tuple

    # if proportional is True, intercept should be 0.0
    _, intercept = result
    if proportional:
        assert intercept == 0.0
# End program