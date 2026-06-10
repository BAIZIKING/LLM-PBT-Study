from hypothesis import given, strategies as st
from statistics import geometric_mean
from math import isclose, prod

# Generate a variety of valid inputs including edge cases:
# - Non-empty sequences/iterables of floats
# - Mixture of small, large, positive values 
# - Repeating decimals, integers, integer-valued floats
# Avoid invalid inputs:
# - Empty sequences 
# - Sequences containing 0, negative numbers, non-numeric types
@given(st.lists(st.floats(min_value=1e-8, allow_infinity=False, allow_nan=False), min_size=1))
def test_geometric_mean(data):
    result = geometric_mean(data)
    
    # Check that output is float
    assert isinstance(result, float)
    
    # Check that output equals nth root of product of n elements
    n = len(data)
    expected = prod(data)**(1/n)
    assert isclose(result, expected)
# End program