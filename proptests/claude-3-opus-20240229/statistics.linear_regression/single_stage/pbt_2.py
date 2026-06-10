from hypothesis import given, strategies as st
from statistics import linear_regression
from math import isclose

# Generate a variety of valid inputs, including edge cases like short/long lists, 
# different magnitudes, some nearly constant x values, and proportional relationships.
# Use separate strategies to generate invalid inputs that should raise StatisticsError.
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2).filter(lambda x: len(set(x)) > 1),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
    st.booleans(),
    st.data()
)
def test_linear_regression(x, y, proportional, data):
    assume(len(x) == len(y))
    
    # Test that the return value is a tuple of 2 floats: slope and intercept
    slope, intercept = linear_regression(x, y, proportional=proportional)
    assert isinstance(slope, float)
    assert isinstance(intercept, float)

    # Test that the slope and intercept approximately satisfy the given points
    for xi, yi in zip(x, y):
        assert isclose(yi, slope * xi + intercept, rel_tol=1e-05, abs_tol=1e-08)
    
    if proportional:
        assert isclose(intercept, 0.0)
    
    # Test that StatisticsError is raised for < 2 data points
    with raises(StatisticsError):
        linear_regression(x[:1], y[:1])
    
    # Test that StatisticsError is raised when x is constant 
    assume(len(set(x)) > 1)  # Ensure not drawn in previous example
    x_constant = [x[0]] * len(x)
    with raises(StatisticsError):  
        linear_regression(x_constant, y)

    # Test mismatched lengths raise StatisticsError
    x_extra = data.draw(st.lists(st.floats(), min_size=1))
    with raises(StatisticsError):
        linear_regression(x + x_extra, y)
# End program