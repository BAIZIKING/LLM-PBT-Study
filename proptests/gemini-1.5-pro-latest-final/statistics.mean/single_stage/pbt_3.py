from hypothesis import given, strategies as st
from statistics import mean, StatisticsError
from fractions import Fraction
from decimal import Decimal

# Summary: Generates lists of varying lengths and numeric types, including edge cases and outliers.
@given(st.lists(st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.fractions(),
    st.decimals()
), min_size=0))
def test_statistics_mean(data):
    if not data:
        with pytest.raises(StatisticsError):
            mean(data)
    else:
        # Calculate expected mean using sum and length
        expected_mean = sum(data) / len(data)
        
        # Handle different numeric types
        if all(isinstance(x, int) for x in data):
            assert mean(data) == expected_mean
        elif all(isinstance(x, float) for x in data):
            assert math.isclose(mean(data), expected_mean)
        elif all(isinstance(x, Fraction) for x in data):
            assert mean(data) == expected_mean
        elif all(isinstance(x, Decimal) for x in data):
            assert mean(data) == expected_mean
# End program