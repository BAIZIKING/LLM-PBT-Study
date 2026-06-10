from hypothesis import given, strategies as st
import statistics as stats

# The strategy here is to generate lists of unique integers with length at least 2 and
# also single boolean value for proportional attribute. We ensure inputs x and y are unique
# to avoid constant value for independent variable x as per the API documentation.
@given(
    st.lists(st.integers(), min_size=2, unique=True), 
    st.lists(st.integers(), min_size=2, unique=True), 
    st.booleans()
)
def test_statistics_linear_regression(x, y, p):
    # First, ensure the lengths of x and y are the same.
    assert len(x) == len(y)
    
    # Run the linear regression.
    result = stats.linear_regression(x, y, proportional=p)

    # Ensure we get two results back (slope and intercept).
    assert len(result) == 2
    
    # Ensure the slope and intercept are numerical values (float).
    slope, intercept = result
    assert isinstance(slope, float)
    assert isinstance(intercept, float)
# End program