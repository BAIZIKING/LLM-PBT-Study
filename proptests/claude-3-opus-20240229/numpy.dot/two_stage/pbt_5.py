from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)), 
       st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_numpy_dot_output_shape(a, b):
    result = np.dot(a, b)
    assert result.shape == np.broadcast(a, b).shape

@given(st.arrays(np.float64, shape=st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_numpy_dot_1d_inner_product(a):
    result = np.dot(a, a)
    assert isinstance(result, np.float64)
    assert np.isclose(result, np.sum(a * a))

@given(st.arrays(np.float64, shape=(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)),
       st.arrays(np.float64, shape=(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_numpy_dot_2d_matrix_multiplication(a, b):
    result = np.dot(a, b)
    assert result.shape == (a.shape[0], b.shape[1])
    assert np.allclose(result, np.matmul(a, b))

@given(st.floats(allow_nan=False, allow_infinity=False),
       st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_numpy_dot_scalar_array(scalar, arr):
    result = np.dot(scalar, arr)
    assert result.shape == arr.shape
    assert np.allclose(result, scalar * arr)

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5)), elements=st.floats(allow_nan=False, allow_infinity=False)),
       st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_numpy_dot_higher_dimensions(a, b):
    result = np.dot(a, b)
    assert result.shape == a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
    assert np.allclose(result, np.einsum('...ij,...jk->...ik', a, b))
# End program