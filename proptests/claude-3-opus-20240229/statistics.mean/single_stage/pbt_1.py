from hypothesis import given, strategies as st
from statistics import mean
import math

# Generate a wide variety of numeric input data including floats, decimals, fractions 
# and integers (both positive and negative). Use composite strategies to generate 
# lists of varying lengths. Include edge cases like empty lists which should raise
# an exception.
@given(st.one_of(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
    st.lists(st.decimals(allow_nan=False, allow_infinity=False), min_size=1), 
    st.lists(st.fractions(), min_size=1),
    st.lists(st.integers(), min_size=1),
    st.lists(st.floats(), max_size=0)
))
def test_mean(data):
    try:
        result = mean(data)
        assert isinstance(result, (float, int, Fraction, Decimal))
        assert math.isclose(result, sum(data)/len(data), rel_tol=1e-9)
    except StatisticsError:
        assert len(data) == 0
# End program