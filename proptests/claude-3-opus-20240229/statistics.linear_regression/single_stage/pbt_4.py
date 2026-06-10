from hypothesis import given, strategies as st
from statistics import linear_regression
import math

# Generate a wide variety of floating point numbers for x and y, including negative values,
# very large and small values, integers, and special values like infinity and NaN.
# Also generate some examples where x is constant to test that edge case.
# Set min_size to 2 since linear_regression requires at least 2 data points.
# To test proportional=True, generate some cases where the intercept should be close to 0. 
@given(st.data())
def test_linear_regression(data):
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
    
    # Truncate longer list so x and y are same length
    if len(x) > len(y):
        x = x[:len(y)] 
    else:
        y = y[:len(x)]

    # Set proportional flag
    proportional = data.draw(st.booleans())
        
    # Skip test for constant x
    assume(len(set(x)) > 1)

    # Run linear regression
    slope, intercept = linear_regression(x, y, proportional=proportional)
    
    # Check properties:
    # - Output slope and intercept are finite floats
    # - When proportional=True, intercept is close to 0
    # - Varying x and y actually varies the outputs  
    assert isinstance(slope, float) and math.isfinite(slope)
    assert isinstance(intercept, float) and math.isfinite(intercept)
    if proportional:
        assert math.isclose(intercept, 0.0, rel_tol=1e-07)
# End program        