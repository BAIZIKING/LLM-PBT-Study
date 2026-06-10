from hypothesis import given, strategies as st
import numpy as np

# Define strategy for generating arrays with limited size and element range
array_strategy = st.arrays(dtype=np.float64, 
                           shape=st.tuples(st.integers(1, 5), st.integers(1, 5)),
                           elements=st.floats(min_value=-1e5, max_value=1e5))

@given(array_strategy)
def test_sum_order_invariant(arr):
    # Shuffle array and compare sum
    shuffled_arr = np.random.permutation(arr.copy())
    assert np.sum(arr) == np.sum(shuffled_arr)

@given(array_strategy)
def test_sum_axis_none_equals_flattened(arr):
    # Compare sum with axis=None to sum of flattened array
    assert np.sum(arr, axis=None) == np.sum(arr.flatten())

@given(st.data())
def test_sum_empty_is_zero(data):
    # Generate empty array of any shape and dtype
    empty_arr = data.draw(st.arrays(dtype=st.sampled_from(np.sctypes['float']), shape=st.tuples(st.integers(0, 5), st.integers(0, 5))))
    assert np.sum(empty_arr) == 0

@given(array_strategy, st.integers(0, 1))
def test_sum_axis_equals_subarray_sum(arr, axis):
    # Compare sum along axis to sum of sub-arrays
    subarray_sums = [np.sum(sub_arr) for sub_arr in np.split(arr, arr.shape[axis], axis=axis)]
    assert np.allclose(np.sum(arr, axis=axis), subarray_sums)

@given(array_strategy, st.floats(min_value=-1e5, max_value=1e5))
def test_sum_initial_offset(arr, initial_value):
    # Compare sum with and without initial value
    assert np.sum(arr, initial=initial_value) == np.sum(arr) + initial_value
# End program