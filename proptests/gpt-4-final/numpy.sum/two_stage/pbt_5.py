from hypothesis import given, strategies as st, assume
from hypothesis.extra.numpy import arrays
import numpy as np

@given(arrays(dtype=float, shape=st.integers(min_value=1, max_value=10)))
def test_consistency_dtype(input_arr):
    result = np.sum(input_arr)
    assert type(result) is np.float64
    
@given(arrays(dtype=float, shape=st.integers(min_value=1, max_value=10)))
def test_summation_accuracy(input_arr):
    assert np.sum(input_arr) == sum(input_arr) 

@given(arrays(dtype=float, shape=(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
def test_dimension_reduction(input_arr):
    result = np.sum(input_arr, axis=1)
    assert input_arr.ndim - result.ndim == 1

@given(st.integers(), arrays(dtype=int, shape=st.integers(min_value=1, max_value=10)))
def test_initial_value(initial, input_arr):
    result = np.sum(input_arr, initial=initial)
    assert result == sum(input_arr) + initial  

@given(arrays(dtype=bool, shape=st.integers(min_value=1, max_value=10)),
       arrays(dtype=float, shape=st.integers(min_value=1, max_value=10)))
def test_where_parameter(where, input_arr):
    assume(len(where) == len(input_arr))
    result = np.sum(input_arr, where=where)
    expected = sum(elem for (elem, cond) in zip(input_arr, where) if cond)
    assert result == expected 