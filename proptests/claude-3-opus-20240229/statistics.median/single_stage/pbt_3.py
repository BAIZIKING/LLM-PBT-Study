from hypothesis import given, strategies as st
from statistics import median, StatisticsError

# Summary: Generate a wide variety of numeric data sequences and iterables to test median.
# Include edge cases like empty iterables, single element sequences, and large lists.
# Check that:
# 1. Result equals middle value for odd number of data points 
# 2. Result equals average of two middle values for even number of data points
# 3. StatisticsError is raised for an empty data input
@given(st.one_of(
    st.lists(st.integers(), min_size=0, max_size=1000), 
    st.iterables(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=1000)
))
def test_statistics_median(data):
    n = len(data)
    if n == 0:
        try:
            median(data)
            assert False, "Expected StatisticsError for empty data"
        except StatisticsError:
            pass
    else:
        sorted_data = sorted(data)
        if n % 2 == 1:
            assert median(data) == sorted_data[n//2]
        else:
            assert median(data) == (sorted_data[n//2 - 1] + sorted_data[n//2])/2
# End program