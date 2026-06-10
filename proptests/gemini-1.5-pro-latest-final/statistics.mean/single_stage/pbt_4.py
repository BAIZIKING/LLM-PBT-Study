from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varying lengths with different numeric types, including edge cases like empty lists and lists with outliers.
@given(st.lists(elements=st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.fractions(),
    st.decimals()
), min_size=0))
def test_statistics_mean(data):
    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.mean(data)
    else:
        calculated_mean = statistics.mean(data)
        expected_mean = sum(data) / len(data)
        assert calculated_mean == expected_mean
# End program