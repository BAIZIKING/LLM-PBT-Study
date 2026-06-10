from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists with varying lengths, data types, sortedness, and outliers.
@given(st.lists(st.one_of(st.floats(), st.integers()), min_size=0))
def test_statistics_median(data):
    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.median(data)
    elif len(data) == 1:
        assert statistics.median(data) == data[0]
    else:
        sorted_data = sorted(data)
        midpoint = len(data) // 2
        if len(data) % 2 == 1:
            assert statistics.median(data) == sorted_data[midpoint]
        else:
            expected_median = (sorted_data[midpoint - 1] + sorted_data[midpoint]) / 2
            assert statistics.median(data) == pytest.approx(expected_median)
# End program