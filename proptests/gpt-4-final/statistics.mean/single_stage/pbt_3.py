from hypothesis import given, strategies as st
from statistics import mean
import pytest

# Testing a wide variety of inputs and edge cases for the statistics.mean function
@given(st.lists(st.one_of(st.integers(), st.floats(allow_infinity=False, allow_nan=False), st.fractions(), st.decimals(allow_nan=False, allow_infinity=False)), min_size=1))
def test_statistics_mean(data):
    # If the length of data is 1, the mean should equal the only element in it
    if len(data) == 1:
        assert mean(data) == data[0]
    else:
        # Else the mean should fall within the range of the data
        assert min(data) <= mean(data) <= max(data)

# Testing the edge case where the input data is empty, which should raise a StatisticsError
@given(st.lists(st.integers(), min_size=0, max_size=0))
def test_statistics_mean_empty_data(data):
    with pytest.raises(StatisticsError):
        mean(data)