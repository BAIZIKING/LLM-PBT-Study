from hypothesis import given, strategies as st
from statistics import mean, StatisticsError
from fractions import Fraction
from decimal import Decimal

# Generate a variety of input types and edge cases to thoroughly test mean():
# - Empty iterables to check the StatisticsError is raised
# - Iterables of integers, floats, fractions, and decimals 
# - Iterables of positive and negative numbers
# - Very large and small numbers
@given(st.one_of(
    st.lists(st.nothing(), max_size=0),
    st.lists(st.integers()),
    st.lists(st.floats(allow_infinity=False, allow_nan=False)),
    st.lists(st.fractions()),
    st.lists(st.decimals(allow_infinity=False, allow_nan=False)),
))
def test_mean(data):
    try:
        result = mean(data)
        # Check mean is sum(data)/len(data)
        assert result == sum(data)/len(data)
        # Check return type matches input type
        assert isinstance(result, (float, Fraction, Decimal))
        # Check mean is between min and max of data (inclusive)
        if len(data) > 0:
            assert min(data) <= result <= max(data)
    except StatisticsError:
        # Check exception is raised iff data is empty
        assert len(data) == 0
# End program