from hypothesis import given, strategies as st
import statistics

# Summary: Generates diverse data types, including empty lists and outliers, to test mean calculation and edge cases.
@given(st.one_of(
    st.lists(st.integers()),
    st.lists(st.floats(allow_nan=False, allow_infinity=False)),
    st.lists(st.fractions()),
    st.lists(st.decimals()),
    st.just([]),  # Empty list
))
def test_statistics_mean(data):
    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.mean(data)
    else:
        # Calculate expected mean
        expected_mean = sum(data) / len(data)
        assert type(statistics.mean(data)) == type(expected_mean)  # Type consistency
        assert statistics.mean(data) == expected_mean  # Calculation accuracy

# End program