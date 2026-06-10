from hypothesis import given, strategies as st
from statistics import linear_regression
from hypothesis.strategies import lists, floats, just, booleans
from pytest import raises
from statistics import StatisticsError

# Generating lists of floats for x and y with same length of at least two, and booleans for proportional 
@given(x=lists(floats(allow_infinity=False, allow_nan=False), min_size=2),
       y=lists(floats(allow_infinity=False, allow_nan=False), min_size=2), 
       proportional=booleans())
def test_statistics_linear_regression(x, y, proportional):

    # Making sure x and y have the same amount of elements
    if len(x) != len(y):
        y = y[:len(x)]
        
    # If x is constant, check if StatisticsError is raised 
    if len(set(x)) == 1:
        with raises(StatisticsError):
            linear_regression(x, y, proportional=proportional)
    else:
        slope, intercept = linear_regression(x, y, proportional=proportional)
        
        # Check if returned values are floats or integers
        assert isinstance(slope, (float, int))
        assert isinstance(intercept, (float, int))

        # If proportional is true, the intercept should be 0.0
        if proportional:
            assert intercept == 0.0

# End program