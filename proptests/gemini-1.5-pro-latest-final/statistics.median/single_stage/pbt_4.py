from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varied sizes with integers, floats, and decimals, 
#          including empty lists and ordered/unordered lists.
@given(st.lists(elements=st.one_of(st.integers(), st.floats(allow_nan=False)),
                 min_size=0,
                 max_size=100),
       st.booleans())
def test_statistics_median(data, is_sorted):
    if is_sorted:
        data.sort()  # Test with sorted data
    
    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.median(data)
    else:
        calculated_median = statistics.median(data)
        data.sort()
        midpoint = len(data) // 2
        if len(data) % 2 == 1:
            expected_median = data[midpoint]
        else:
            expected_median = (data[midpoint - 1] + data[midpoint]) / 2
        assert calculated_median == expected_median

# End program