from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_dot(data):
    scalar = data.draw(st.integers())
    one_d_array = data.draw(st.lists(st.integers(), min_size=1, max_size=5))
    two_d_array = data.draw(st.lists(st.lists(st.integers(), min_size=1, max_size=5), min_size=1, max_size=5))
    
    # Test with scalar inputs
    assert np.dot(scalar, scalar) == scalar * scalar, "Failed with scalar inputs"
    
    # Test with 1-D array inputs 
    assert np.dot(one_d_array, one_d_array) == sum(i*i for i in one_d_array), "Failed with 1-D array inputs"

    # Test with 2-D array inputs; We are comparing 2D dot product with @ operator for matrix multiplication
    if len(two_d_array) == len(two_d_array[0]): # Ensuring it's a square matrix
        assert np.allclose(np.dot(two_d_array, two_d_array), np.array(two_d_array) @ np.array(two_d_array)), "Failed with 2-D array inputs"

    # Test with N-D array and 1-D array inputs; Here, we assume N=2 for simplicity.
    if len(two_d_array[0]) == len(one_d_array): # Ensuring matrix multiplication is possible
        assert np.allclose(np.dot(two_d_array, one_d_array), np.sum(np.array(two_d_array) * np.array(one_d_array), axis=-1)), "Failed with N-D array and 1-D array inputs"