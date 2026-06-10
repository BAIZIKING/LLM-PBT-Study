from hypothesis import given, strategies as st
from statistics import variance
from decimal import Decimal
from fractions import Fraction

# Generate lists of various numeric types with at least 2 elements.
# Include integers, floats, Decimals, and Fractions.
# Sometimes pass the mean to test the xbar parameter.
# Test edge cases like very large/small values and nearly equal values.
@given(st.data()) 
def test_variance(data):
    elements = data.draw(st.one_of(
        st.lists(st.integers(), min_size=2),
        st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2),
        st.lists(st.fractions(), min_size=2),
        st.lists(st.decimals(allow_infinity=False, allow_nan=False), min_size=2)))
    
    xbar = data.draw(st.booleans())
    if xbar:
        m = sum(elements) / len(elements)
        var = variance(elements, xbar=m)
    else:
        var = variance(elements)

    assert isinstance(var, (float, Decimal, Fraction))
    assert var >= 0
    n = len(elements)
    diffs = [(x - sum(elements)/n)**2 for x in elements]
    assert abs(var - sum(diffs)/(n-1)) < 1e-8
# End program    