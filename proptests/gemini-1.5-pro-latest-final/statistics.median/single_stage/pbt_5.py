from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of numeric data with varying lengths, types, and order
@given(st.lists(elements=st.one_of(st.integers(), st.floats()),
                min_size=0,
                max_size=20,
                unique=False).map(sorted),  # Include sorted and unsorted lists
       st.booleans())  # To control outlier inclusion
def test_statistics_median(data, include_outlier):
    if include_outlier:
        # Add an outlier at the beginning
        data.insert(0, 1000 * data[-1])  

    if not data:
        with pytest.raises(statistics.StatisticsError):
            statistics.median(data)
    else:
        median_value = statistics.median(data)
        if len(data) % 2 == 1:
            # Odd length list - median should be middle element
            assert median_value == data[len(data) // 2]
        else:
            # Even length list - median should be average of middle two
            mid_1, mid_2 = data[len(data) // 2 - 1], data[len(data) // 2]
            assert median_value == (mid_1 + mid_2) / 2
        
        # Check data type consistency
        assert type(median_value) in (int, float)
# End program