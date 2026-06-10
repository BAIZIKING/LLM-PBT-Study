from hypothesis import given, strategies as st
from statistics import mean, StatisticsError

# Summary: Generate a wide variety of numeric data types and edge cases to 
# comprehensively test the statistics.mean function. Inputs generated include:
# - Empty iterables which should raise StatisticsError
# - Iterables of various numeric types: int, float, Fraction, Decimal
# - Iterables of arbitrary size from 1-100 elements
# - Iterables containing a mix of numeric types
# The following properties are checked, as inferred from the documentation:
# - StatisticsError is raised for an empty data iterable 
# - The result is always a numeric type
# - The result equals the sum of the input data divided by number of data points
@given(st.one_of(
    st.lists(st.one_of(st.integers(), st.floats(), st.fractions(), st.decimals()), min_size=1, max_size=100),
    st.lists(st.nothing(), max_size=0)
))
def test_statistics_mean(data):
    if len(data) == 0:
        try:
            mean(data)
            assert False, "Expected StatisticsError for empty input"
        except StatisticsError:
            pass
    else:
        result = mean(data)
        assert isinstance(result, (int, float, Fraction, Decimal))
        assert result == sum(data) / len(data)
# End program