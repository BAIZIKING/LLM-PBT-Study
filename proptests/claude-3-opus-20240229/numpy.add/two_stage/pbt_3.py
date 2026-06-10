from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_add_shape_property(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(st.data())
def test_numpy_add_elementwise_property(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    result = np.add(x1, x2)
    assert np.all(result == x1 + x2)

@given(st.floats(-1e6, 1e6), st.floats(-1e6, 1e6))
def test_numpy_add_scalar_property(x1, x2):
    result = np.add(x1, x2)
    assert isinstance(result, np.float64)
    assert result == x1 + x2

@given(st.data())
def test_numpy_add_out_property(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    out = np.zeros(np.broadcast(x1, x2).shape)
    result = np.add(x1, x2, out=out)
    assert result is out
    assert np.all(result == x1 + x2)

@given(st.data())
def test_numpy_add_where_property(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(*[st.integers(0, 10) for _ in range(data.draw(st.integers(0, 5)))]), elements=st.floats(-1e6, 1e6)))
    where = data.draw(st.arrays(bool, shape=np.broadcast(x1, x2).shape))
    out = np.zeros(np.broadcast(x1, x2).shape)
    result = np.add(x1, x2, out=out, where=where)
    assert np.all(result[where] == (x1 + x2)[where])
    assert np.all(result[~where] == out[~where])
# End program