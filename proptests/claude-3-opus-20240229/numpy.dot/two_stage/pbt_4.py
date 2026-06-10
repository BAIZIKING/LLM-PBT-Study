from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_dot_shape(data):
    shape_a = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=5))
    shape_b = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=5))
    a = data.draw(st.arrays(np.float64, shape=shape_a))
    b = data.draw(st.arrays(np.float64, shape=shape_b))
    
    try:
        result = np.dot(a, b)
        assert result.shape == np.broadcast(a, b).shape
    except ValueError:
        assert a.shape[-1] != b.shape[-2]

@given(st.data())
def test_numpy_dot_1d_vectors(data):
    size = data.draw(st.integers(min_value=1, max_value=100))
    a = data.draw(st.arrays(np.float64, shape=size))
    b = data.draw(st.arrays(np.float64, shape=size))
    
    result = np.dot(a, b)
    assert np.isclose(result, np.sum(a * b))

@given(st.data())
def test_numpy_dot_2d_matrices(data):
    rows = data.draw(st.integers(min_value=1, max_value=10))
    cols = data.draw(st.integers(min_value=1, max_value=10))
    common_dim = data.draw(st.integers(min_value=1, max_value=10))
    
    a = data.draw(st.arrays(np.float64, shape=(rows, common_dim)))
    b = data.draw(st.arrays(np.float64, shape=(common_dim, cols)))
    
    result = np.dot(a, b)
    expected = np.matmul(a, b)
    assert np.allclose(result, expected)

@given(st.data())
def test_numpy_dot_scalar(data):
    scalar = data.draw(st.floats(min_value=-1e10, max_value=1e10))
    array = data.draw(st.arrays(np.float64, shape=data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=5))))
    
    result = np.dot(scalar, array)
    assert np.allclose(result, scalar * array)

@given(st.data())
def test_numpy_dot_sum_product(data):
    shape_a = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=2, max_size=5))
    shape_b = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=2, max_size=5))
    
    a = data.draw(st.arrays(np.float64, shape=shape_a))
    b = data.draw(st.arrays(np.float64, shape=shape_b))
    
    try:
        result = np.dot(a, b)
        assert np.allclose(result, np.sum(a[..., np.newaxis] * b[..., np.newaxis, :, :], axis=-2))
    except ValueError:
        assert a.shape[-1] != b.shape[-2]
# End program