from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_add_shape(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False))
def test_numpy_add_scalars(x1, x2):
    result = np.add(x1, x2)
    assert isinstance(result, float)

@given(st.data())
def test_numpy_add_elementwise(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    result = np.add(x1, x2)
    assert np.array_equal(result, x1 + x2)

@given(st.data())
def test_numpy_add_out(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    out = np.zeros(np.broadcast(x1, x2).shape)
    result = np.add(x1, x2, out=out)
    assert result is out

@given(st.data())
def test_numpy_add_where(data):
    x1 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    x2 = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
    where = data.draw(st.arrays(bool, shape=np.broadcast(x1, x2).shape))
    out = np.zeros(np.broadcast(x1, x2).shape)
    result = np.add(x1, x2, out=out, where=where)
    assert np.array_equal(result[where], (x1+x2)[where])
    assert np.array_equal(result[~where], out[~where])
# End program