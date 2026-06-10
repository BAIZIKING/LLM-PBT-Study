from hypothesis import given, strategies as st
from statistics import median, StatisticsError

# Summary: Generate a wide variety of numeric lists, including empty lists, lists 
# with duplicates, sorted/unsorted lists, lists with negative numbers, and large lists.
# Test that:
# - median raises StatisticsError for an empty list
# - median returns the middle element for odd-length lists
# - median returns the average of the two middle elements for even-length lists
# - median is less than or equal to the max element 
# - median is greater than or equal to the min element
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=1000))
def test_median(data):
    if len(data) == 0:
        try:
            median(data)
            assert False, "Expected StatisticsError for empty data"
        except StatisticsError:
            pass
    else:
        result = median(data)
        sorted_data = sorted(data)
        n = len(data)
        if n % 2 == 1:
            assert result == sorted_data[n//2]
        else:
            assert result == (sorted_data[n//2 - 1] + sorted_data[n//2])/2
        assert result <= max(data)
        assert result >= min(data)
# End program        