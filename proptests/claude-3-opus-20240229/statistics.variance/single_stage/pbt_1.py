from hypothesis import given, strategies as st
from statistics import variance
from math import isclose

# Generate a wide variety of numeric data types and edge cases:
# - Lists of floats, ints, fractions and decimals
# - Different length lists >= 2 elements 
# - Large and small magnitude numbers
# - Negative and positive numbers
# Also optionally generate a mean value to pass as the xbar parameter.
@given(st.data())
def test_variance(data):
    values = data.draw(st.lists(st.one_of(
        st.floats(allow_nan=False, allow_infinity=False), 
        st.integers(), 
        st.fractions(),
        st.decimals(allow_nan=False, allow_infinity=False)),
        min_size=2))
    xbar = data.draw(st.one_of(
        st.none(), 
        st.floats(allow_nan=False, allow_infinity=False)))

    # Test that variance matches a manual variance calculation
    mean = sum(values) / len(values) if xbar is None else xbar
    squared_diffs = [(x - mean)**2 for x in values]
    expected = sum(squared_diffs) / (len(values) - 1)
    
    assert isclose(variance(values, xbar), expected)

    # Test that variance >= 0 
    assert variance(values, xbar) >= 0

    # Test that variance of a constant list is 0
    if all(x == values[0] for x in values):
        assert variance(values, xbar) == 0
# End program        