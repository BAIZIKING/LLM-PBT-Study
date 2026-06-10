from hypothesis import given, strategies as st
import statistics
import pytest

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_mean(input_data):
    # Manually calculate the mean
    manual_mean = sum(input_data) / len(input_data)
    
    # Assert that this is equal to the mean calculated by the function
    assert statistics.mean(input_data) == manual_mean

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
def test_statistics_mean_empty_list(input_data):
    # Test that a StatisticsError is raised when the input list is empty
    with pytest.raises(statistics.StatisticsError):
        statistics.mean(input_data)