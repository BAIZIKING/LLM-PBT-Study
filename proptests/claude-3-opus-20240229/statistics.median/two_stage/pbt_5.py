from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.integers()))
def test_median_within_bounds(data):
    if data:
        median = statistics.median(data)
        assert min(data) <= median <= max(data)

@given(st.lists(st.integers()))
def test_median_on_sorted_data(data):
    sorted_data = sorted(data)
    if sorted_data:
        median = statistics.median(sorted_data)
        if len(sorted_data) % 2 == 1:
            assert median == sorted_data[len(sorted_data) // 2]
        else:
            assert median == (sorted_data[len(sorted_data) // 2 - 1] + sorted_data[len(sorted_data) // 2]) / 2

@given(st.lists(st.integers()))
def test_median_invariant_under_permutation(data):
    if data:
        median_original = statistics.median(data)
        median_permuted = statistics.median(data[::-1])
        assert median_original == median_permuted

@given(st.lists(st.integers()), st.integers())
def test_median_invariant_under_element_addition(data, element):
    if data:
        median_original = statistics.median(data)
        data.append(element)
        median_updated = statistics.median(data)
        assert median_original == median_updated or median_updated == element

@given(st.lists(st.integers(), min_size=1, max_size=100))
def test_median_on_identical_elements(data):
    element = data[0]
    data = [element] * len(data)
    assert statistics.median(data) == element
# End program