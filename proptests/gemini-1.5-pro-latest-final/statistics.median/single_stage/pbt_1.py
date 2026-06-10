from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varying lengths with mixed numeric types (integers and floats) to test median calculation for both odd and even lengths, including empty lists and data type consistency.
@given(st.lists(st.one_of(st.integers(), st.floats()), min_size=0))
def test_statistics_median(data):
    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.median(data)
    else:
        sorted_data = sorted(data)
        midpoint = len(data) // 2
        if len(data) % 2:
            expected_median = sorted_data[midpoint]
        else:
            expected_median = (sorted_data[midpoint - 1] + sorted_data[midpoint]) / 2
        assert statistics.median(data) == expected_median
        assert type(statistics.median(data)) in [int, float]
# End program