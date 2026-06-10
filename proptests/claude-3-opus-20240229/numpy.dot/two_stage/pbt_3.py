from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_dot_output_shape(data):
    shape1 = data.draw(st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=2))
    shape2 = data.draw(st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=2))
    a = data.draw(st.arrays(np.float64, shape=shape1))
    b = data.draw(st.arrays(np.float64, shape=shape2))
    out = np.dot(a, b)
    assert out.shape == (a.shape[0], b.shape[1])

@given(st.arrays(np.float64, shape=st.integers(min_value=1, max_value=100)))
def test_numpy_dot_1d_inner_product(a):
    b = a.copy()
    out = np.dot(a, b)
    assert np.isscalar(out)
    assert out == np.inner(a, b)

@given(st.data())
def test_numpy_dot_2d_matrix_product(data):
    shape1 = data.draw(st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=2))
    shape2 = data.draw(st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=2))
    shape2[0] = shape1[1]  # Ensure compatible dimensions
    a = data.draw(st.arrays(np.float64, shape=shape1))
    b = data.draw(st.arrays(np.float64, shape=shape2))
    out = np.dot(a, b)
    assert out.shape == (a.shape[0], b.shape[1])
    assert np.allclose(out, a @ b)

@given(st.floats(allow_infinity=False, allow_nan=False), st.arrays(np.float64))
def test_numpy_dot_scalar_multiplication(scalar, arr):
    out = np.dot(scalar, arr)
    assert out.shape == arr.shape
    assert np.allclose(out, scalar * arr)

@given(st.data())
def test_numpy_dot_sum_product(data):
    shape1 = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=3, max_size=3))
    shape2 = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=4, max_size=4))
    shape2[-2] = shape1[-1]  # Ensure compatible dimensions
    a = data.draw(st.arrays(np.float64, shape=shape1))
    b = data.draw(st.arrays(np.float64, shape=shape2))
    out = np.dot(a, b)
    assert out.shape == a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
    for index in np.ndindex(out.shape):
        i, j, k, m = index
        assert np.isclose(out[i, j, k, m], np.sum(a[i, j, :] * b[k, :, m]))
# End program