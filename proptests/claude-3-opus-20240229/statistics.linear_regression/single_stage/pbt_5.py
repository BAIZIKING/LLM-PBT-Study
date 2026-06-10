from hypothesis import given, strategies as st
from statistics import linear_regression
from math import isclose

# Summary:
# Generate random input data for x and y of varying lengths
# between 2 and 100 elements. Include both positive and negative floats.
# Check the following properties:
# 1. Returned slope and intercept are finite floats 
# 2. Length of x and y are equal
# 3. If x and y are directly proportional and proportional=True,
#    the y-intercept should be close to 0.
# 4. If x is constant, a StatisticsError is raised
@given(st.data())
def test_statistics_linear_regression(data):
    x = data.draw(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=2, max_size=100))
    
    # Assume 90% of the time x and y have some correlation
    # and 10% of the time they are directly proportional
    proportional = data.draw(st.booleans(0.1))
    if proportional:
        c = data.draw(st.floats(min_value=-1e6, max_value=1e6))
        y = [xi * c for xi in x]
    else:  
        y = data.draw(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=len(x), max_size=len(x)))

    try:
        slope, intercept = linear_regression(x, y, proportional=proportional)
        
        # Check properties
        assert isinstance(slope, float) and slope != float('inf')
        assert isinstance(intercept, float) and intercept != float('inf')
        assert len(x) == len(y)
        if proportional:
            assert isclose(intercept, 0.0, rel_tol=1e-6)
    
    except StatisticsError:
        # If x is constant, a StatisticsError should be raised
        assert all(xi == x[0] for xi in x)
# End program