from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1))
def test_output_length_equals_input_length(arr):
    result = np.cumsum(arr)
    assert len(result) == len(arr)

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1))
def test_first_element_equals_input_first_element(arr):
    result = np.cumsum(arr)
    assert result[0] == arr[0]

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1))
def test_last_element_equals_sum_of_input(arr):
    result = np.cumsum(arr)
    assert result[-1] == sum(arr)

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1))
def test_output_elements_greater_than_or_equal_to_input_elements(arr):
    result = np.cumsum(arr)
    assert all(result[i] >= arr[i] for i in range(len(arr)))

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=2))
def test_difference_between_adjacent_output_elements_equals_input_element(arr):
    result = np.cumsum(arr)
    assert all(result[i] - result[i-1] == arr[i] for i in range(1, len(arr)))
# End program