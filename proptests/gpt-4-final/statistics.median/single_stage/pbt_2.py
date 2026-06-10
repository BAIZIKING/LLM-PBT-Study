
from hypothesis import given, strategies as st
import statistics
import pytest

def even_length(values):
    # Helper function to check if the length of list is even
    return len(values) % 2 == 0

@given(st.lists(st.integers(), min_size=0, max_size=100))
def test_statistics_median(values):
    # Property test to check the statistic.median() function behavior
    if not values:
        # If the list is empty, it should raise an exception
        with pytest.raises(statistics.StatisticsError):
            statistics.median(values)
    elif even_length(values):
        # If the list length is even, the median is the average of two middle elements
        sorted_values = sorted(values)
        mid = len(values) // 2
        expected_median = (sorted_values[mid - 1] + sorted_values[mid]) / 2
        assert statistics.median(values) == expected_median
    else:
        # If the list length is odd, the median is the middle element
        sorted_values = sorted(values)
        mid = len(values) // 2
        expected_median = sorted_values[mid]
        assert statistics.median(values) == expected_median
# End program