from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays, array_shapes
import numpy as np

@given(st.data())
def test_numpy_dot(data):
    # Generating test cases
    shape_a = data.draw(array_shapes(min_dims=1, max_dims=3, min_side=1))
    shape_b = data.draw(array_shapes(min_dims=1, max_dims=3, min_side=1))
    if len(shape_b) > 1:
        shape_b = shape_b[:-2] + shape_a[-1:]
    a = data.draw(arrays(dtype=float, shape=shape_a))
    b = data.draw(arrays(dtype=float, shape=shape_b))
    
    # Checking properties
    result = np.dot(a, b)
    if len(shape_a) == 1 and len(shape_b) == 1:  # if a and b are both 1-D arrays
        assert np.allclose(result, sum(a[i] * b[i] for i in range(len(a))))
    elif len(shape_a) == 2 and len(shape_b) == 2:  # if a and b are both 2-D arrays
        assert np.allclose(result, np.matmul(a, b))
    elif len(shape_a) > 1 and len(shape_b) == 1:  # if a is an N-D array and b is a 1-D array
        assert result.shape == shape_a[:-1]
    elif len(shape_a) > 1 and len(shape_b) > 1:  # if a is an N-D array and b is an M-D array
        assert result.shape == shape_a[:-1] + shape_b[:-2]