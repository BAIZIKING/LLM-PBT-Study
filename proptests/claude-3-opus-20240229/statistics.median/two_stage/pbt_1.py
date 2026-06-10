from hypothesis import given, strategies as st
from statistics import median, StatisticsError

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_in_data_odd_length(data):
    if len(data) % 2 == 1:
        assert median(data) in data

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100))
def test_median_average_middle_elements_even_length(data):
    if len(data) % 2 == 0:
        sorted_data = sorted(data)
        middle_left = sorted_data[len(data) // 2 - 1]
        middle_right = sorted_data[len(data) // 2]
        assert median(data) == (middle_left + middle_right) / 2

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_greater_than_equal_min(data):
    assert median(data) >= min(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_less_than_equal_max(data):
    assert median(data) <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=0))
def test_median_empty_data_raises_statistics_error(data):
    try:
        median(data)
        assert False, "Expected StatisticsError"
    except StatisticsError:
        pass
# End program