from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays with controlled size and element range
array_strategy = st.arrays(np.float64, st.tuples(st.integers(0, 10), st.integers(0, 10)), 
                           elements=st.floats(min_value=-1e5, max_value=1e5))
constant_strategy = st.floats(min_value=-1e2, max_value=1e2) 

@given(array_strategy)
def test_sum_empty_array(arr):
    empty_arr = arr[:0]  # Create an empty view of the array
    assert np.sum(empty_arr) == 0

@given(array_strategy)
def test_sum_commutativity(arr):
    shuffled_arr = arr.copy()  # Ensure we don't modify the original array
    np.random.shuffle(shuffled_arr)
    assert np.sum(arr) == np.sum(shuffled_arr)

@given(array_strategy)
def test_sum_associativity(arr):
    if arr.ndim >= 2:
        sum_all_at_once = np.sum(arr)
        sum_axis_0_then_1 = np.sum(np.sum(arr, axis=0), axis=1)
        sum_axis_1_then_0 = np.sum(np.sum(arr, axis=1), axis=0)
        assert np.allclose(sum_all_at_once, sum_axis_0_then_1) 
        assert np.allclose(sum_all_at_once, sum_axis_1_then_0)

@given(array_strategy, constant_strategy)
def test_sum_distributivity(arr, constant):
    scaled_sum = np.sum(arr * constant)
    sum_then_scale = np.sum(arr) * constant
    assert np.allclose(scaled_sum, sum_then_scale)

@given(st.data())
def test_sum_monotonicity(data):
    arr1 = data.draw(array_strategy)
    arr2 = data.draw(array_strategy)
    # Ensure arrays have the same shape for element-wise comparison
    assert arr1.shape == arr2.shape
    if np.all(arr1 >= arr2):
        assert np.sum(arr1) >= np.sum(arr2)

# End program