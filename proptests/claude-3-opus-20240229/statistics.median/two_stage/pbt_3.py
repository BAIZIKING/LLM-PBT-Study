from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_within_range(data):
    median = statistics.median(data)
    assert min(data) <= median <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1).map(sorted))
def test_median_on_sorted_data(data):
    median = statistics.median(data)
    n = len(data)
    if n % 2 == 1:
        assert median == data[n // 2]
    else:
        assert median == (data[n // 2 - 1] + data[n // 2]) / 2

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_permutation_invariance(data):
    median1 = statistics.median(data)
    data_permuted = data.copy()
    st.permutations(data_permuted).example()
    median2 = statistics.median(data_permuted)
    assert median1 == median2

@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(min_value=1, max_value=100))
def test_median_identical_elements(value, size):
    data = [value] * size
    assert statistics.median(data) == value

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_median_element_addition(data, new_element):
    old_median = statistics.median(data)
    if new_element < old_median:
        data.append(new_element)
        new_median = statistics.median(data)
        assert new_median <= old_median
    elif new_element > old_median:
        data.append(new_element)
        new_median = statistics.median(data)
        assert new_median >= old_median
# End program