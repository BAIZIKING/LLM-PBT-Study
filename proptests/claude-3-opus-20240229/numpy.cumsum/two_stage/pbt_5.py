from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_output_size(arr):
    result = np.cumsum(arr)
    assert len(result) == len(arr)

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_1d_input_1d_output(arr):
    result = np.cumsum(arr)
    assert result.ndim == 1

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_last_element_sum(arr):
    result = np.cumsum(arr)
    assert result[-1] == np.sum(arr)

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=5)))
def test_cumulative_sum(arr):
    result = np.cumsum(arr)
    for i in range(len(arr)):
        assert result[i] == np.sum(arr[:i+1])

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=2, max_value=5)))
def test_output_shape(arr):
    result = np.cumsum(arr)
    assert result.shape == arr.shape
# End program