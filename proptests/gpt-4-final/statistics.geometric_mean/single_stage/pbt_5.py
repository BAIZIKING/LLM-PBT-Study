from hypothesis import given, strategies as st, assume
import statistics as stat

MAX_INT_SIZE = 2 ** 31 - 1
MIN_INT_SIZE = 1
MAX_SIZE = 1000

@given(st.lists(st.floats(MIN_INT_SIZE, MAX_INT_SIZE), min_size=1, max_size=MAX_SIZE))
def test_statistics_geometric_mean(data):
    assume(all(x > 0 for x in data))  # Ensure data contains all positive numbers
    result = stat.geometric_mean(data)

    assert isinstance(result, float) # Result should be a floating point number
    assert result <= max(data) and result >= min(data)  # Result should be between min and max of input numbers
    assert result > 0  # Result should be greater than zero, as geometric mean of positive numbers is always positive