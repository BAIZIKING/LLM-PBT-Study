import statistics
from hypothesis import given, strategies as st
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_median(data):
    data.sort()  # Ensure data is sorted
    median = statistics.median(data)

    if len(data) % 2 == 1:
        # If odd, median should be the middle item
        assert median == data[(len(data) // 2)]
    else:
        # If even, median should be average of two middle items
        assert isclose(median, sum(data[(len(data) // 2) - 1:(len(data) // 2) + 1]) / 2)
