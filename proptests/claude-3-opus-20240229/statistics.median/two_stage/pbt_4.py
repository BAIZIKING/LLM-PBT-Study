from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_within_range(data):
    median = statistics.median(data)
    assert min(data) <= median <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1).map(sorted))
def test_median_with_sorted_data(data):
    median = statistics.median(data)
    n = len(data)
    if n % 2 == 1:
        assert median == data[n // 2]
    else:
        assert isclose(median, (data[n // 2 - 1] + data[n // 2]) / 2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_median_with_element_added(data, element):
    median_before = statistics.median(data)
    data.append(element)
    median_after = statistics.median(data)
    assert median_before == median_after or element == median_after

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_with_data_doubled(data):
    median_before = statistics.median(data)
    data.extend(data)
    median_after = statistics.median(data)
    assert median_before == median_after

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_element_property(data):
    median = statistics.median(data)
    n = len(data)
    if n % 2 == 1:
        assert median in data
    else:
        assert any(isclose(median, (a + b) / 2) for a, b in zip(data, data[1:]))
# End program