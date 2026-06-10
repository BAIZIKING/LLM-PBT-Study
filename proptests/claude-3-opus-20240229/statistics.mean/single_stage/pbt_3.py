from hypothesis import given, strategies as st
from statistics import mean, StatisticsError

# Summary: 
# Generate lists of various numeric types including ints, floats, fractions, and decimals.
# Also generate some edge cases like empty lists which should raise an exception.
# Check that the calculated mean matches the expected formula: sum(data) / len(data).
# Confirm that empty input raises StatisticsError.
@given(st.one_of(
    st.lists(st.integers()), 
    st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
    st.lists(st.fractions()),
    st.lists(st.decimals(allow_nan=False, allow_infinity=False)),
    st.builds(list)
))
def test_mean(data):
    try:
        result = mean(data)
        assert result == sum(data) / len(data)
    except StatisticsError:
        assert len(data) == 0
    except TypeError:
        assert len(data) == 0
# End program