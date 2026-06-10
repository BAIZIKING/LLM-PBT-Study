from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100)))
def test_output_size_equals_input_size(arr):
    assert len(np.cumsum(arr)) == len(arr)

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100)))
def test_output_is_1d_if_input_is_1d(arr):
    if arr.ndim == 1:
        assert np.cumsum(arr).ndim == 1

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100)))
def test_last_element_equals_sum(arr):
    assert np.cumsum(arr)[-1] == np.sum(arr)

@given(st.arrays(dtype=np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))),
       st.integers(min_value=0, max_value=1))
def test_output_shape_equals_input_shape_when_axis_specified(arr, axis):
    assert np.cumsum(arr, axis=axis).shape == arr.shape

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100)))
def test_output_elements_greater_than_or_equal_to_input_elements(arr):
    assert np.all(np.cumsum(arr) >= arr)
# End program