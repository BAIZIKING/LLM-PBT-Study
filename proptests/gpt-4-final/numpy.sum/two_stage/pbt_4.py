from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0), st.booleans())
def test_sum_of_all_elements(input_list, dtype, keepdims):
    # Convert list to array
    input_array = np.array(input_list, dtype=dtype)

    # Calculate sum using numpy.sum
    result = np.sum(input_array, keepdims=keepdims)

    # Check if result matches the expected output type
    assert isinstance(result, np.ndarray if keepdims else (np.int64 if dtype == np.int else np.float64))

  
@given(st.lists(st.integers(), min_size=1))
def test_sum_of_elements(input_list):
    # Convert list to array
    input_array = np.array(input_list)

    # Calculate sum using numpy.sum and python's sum function
    np_sum = np.sum(input_array)
    py_sum = sum(input_list)

    # The result from numpy's sum and python's sum should be the same
    assert np_sum == py_sum

  
@given(st.lists(st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=2), min_size=2, max_size=2))
def test_sum_with_axis(input_list):
    # Convert list to array
    input_array = np.array(input_list)

    # When axis=0
    assert np.all(np.sum(input_array, axis=0) == [sum(col) for col in zip(*input_list)])

    # When axis=1
    assert np.all(np.sum(input_array, axis=1) == [sum(row) for row in input_list])

  
@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))
def test_sum_with_keepdims(input_list, keepdims):
    # Convert list to array
    input_array = np.array(input_list)

    # Calculate sum using numpy.sum
    result = np.sum(input_array, keepdims=keepdims)

    # Check if result shape matches the expected output shape
    assert result.shape == (1, ) if keepdims else ()
  

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1), st.sampled_from([np.int, np.float]))
def test_sum_with_dtype(input_list, dtype):
    # Convert list to array
    input_array = np.array(input_list, dtype=dtype)

    # Calculate sum using numpy.sum
    result = np.sum(input_array)

    # Result dtype should match the input dtype
    assert result.dtype == input_array.dtype