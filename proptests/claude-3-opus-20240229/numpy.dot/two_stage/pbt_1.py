from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, shape=st.integers(0, 5), elements=st.floats(-1e6, 1e6)),
       st.arrays(np.float64, shape=st.integers(0, 5), elements=st.floats(-1e6, 1e6)))
def test_numpy_dot_shape(a, b):
    result = np.dot(a, b)
    if a.ndim == 0 or b.ndim == 0:
        assert result.shape == (a + b).shape
    elif a.ndim == 1 and b.ndim == 1:
        assert result.ndim == 0
    else:
        assert result.shape == a.shape[:-1] + b.shape[1:]

@given(st.arrays(np.float64, shape=st.integers(1, 100), elements=st.floats(-1e6, 1e6)),
       st.arrays(np.float64, shape=st.integers(1, 100), elements=st.floats(-1e6, 1e6)))
def test_numpy_dot_inner_product(a, b):
    assume(len(a) == len(b))
    result = np.dot(a, b)
    expected = sum(x * y for x, y in zip(a, b))
    assert np.allclose(result, expected)

@given(st.arrays(np.float64, shape=(st.integers(1, 10), st.integers(1, 10)), elements=st.floats(-1e6, 1e6)),
       st.arrays(np.float64, shape=(st.integers(1, 10), st.integers(1, 10)), elements=st.floats(-1e6, 1e6)))
def test_numpy_dot_matrix_multiplication(a, b):
    assume(a.shape[1] == b.shape[0])
    result = np.dot(a, b)
    expected = np.matmul(a, b)
    assert np.allclose(result, expected)

@given(st.floats(-1e6, 1e6),
       st.arrays(np.float64, shape=st.integers(0, 5), elements=st.floats(-1e6, 1e6)))
def test_numpy_dot_scalar_multiplication(scalar, arr):
    result = np.dot(scalar, arr)
    expected = scalar * arr
    assert np.allclose(result, expected)

@given(st.arrays(np.int32, shape=st.integers(0, 5), elements=st.integers(-1e6, 1e6)),
       st.arrays(np.float64, shape=st.integers(0, 5), elements=st.floats(-1e6, 1e6)))
def test_numpy_dot_output_dtype(a, b):
    result = np.dot(a, b)
    assert result.dtype == np.promote_types(a.dtype, b.dtype)
# End program