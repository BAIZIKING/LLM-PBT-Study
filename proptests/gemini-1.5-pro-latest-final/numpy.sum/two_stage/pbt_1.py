from hypothesis import given, strategies as st
import numpy as np

# Define strategy for generating arrays of floats with controlled size and magnitude
# to avoid overflows and excessive runtimes
@st.composite
def arrays_of_floats(draw, elements=st.floats(allow_nan=False), min_size=0, max_size=100):
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return draw(st.lists(elements, min_size=size, max_size=size))

@given(arrays_of_floats())
def test_sum_empty_array(arr):
    empty_arr = np.array([])
    assert np.sum(empty_arr) == 0

@given(arrays_of_floats(), st.integers(min_value=0, max_value=1))
def test_sum_commutativity(arr, index1):
    index2 = (index1 + 1) % len(arr)
    arr_swapped = arr.copy()
    arr_swapped[index1], arr_swapped[index2] = arr_swapped[index2], arr_swapped[index1]
    assert np.sum(arr) == np.sum(arr_swapped)

@given(arrays_of_floats())
def test_sum_associativity(arr):
    split_point = np.random.randint(1, len(arr))
    first_half = arr[:split_point]
    second_half = arr[split_point:]
    assert np.sum(np.sum(first_half) + np.sum(second_half)) == np.sum(arr)

@given(arrays_of_floats(), st.floats(allow_nan=False))
def test_sum_distributivity(arr, k):
    scaled_arr = k * arr
    assert np.sum(scaled_arr) == k * np.sum(arr)

@given(arrays_of_floats(), arrays_of_floats())
def test_sum_monotonicity(arr1, arr2):
    # Ensure arrays are same length for element-wise comparison
    assert len(arr1) == len(arr2)
    if all(a >= b for a, b in zip(arr1, arr2)):
        assert np.sum(arr1) >= np.sum(arr2)
# End program