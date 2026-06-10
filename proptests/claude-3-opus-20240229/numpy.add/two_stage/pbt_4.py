from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_add_shape(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(st.data())
def test_numpy_add_same_shape(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    result = np.add(x1, x2)
    assert np.array_equal(result, x1 + x2)

@given(st.data())
def test_numpy_add_dtype(data):
    dtype = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float32, np.float64]))
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=dtype, shape=shape))
    x2 = data.draw(st.arrays(dtype=dtype, shape=shape))
    result = np.add(x1, x2)
    assert result.dtype == dtype

@given(st.data())
def test_numpy_add_scalar(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    x2 = data.draw(st.floats(min_value=-1e10, max_value=1e10))
    result = np.add(x1, x2)
    assert np.array_equal(result, x1 + x2)

@given(st.data())
def test_numpy_add_where(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    where = data.draw(st.arrays(dtype=bool, shape=shape))
    result = np.add(x1, x2, where=where)
    expected = np.where(where, x1 + x2, x1)
    assert np.array_equal(result, expected)
# End program