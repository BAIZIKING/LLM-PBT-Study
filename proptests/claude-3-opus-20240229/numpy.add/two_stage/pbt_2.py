from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_output_shape(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape))
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(st.data())
def test_element_wise_sum(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape, elements=st.floats(min_value=-1e6, max_value=1e6)))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape, elements=st.floats(min_value=-1e6, max_value=1e6)))
    result = np.add(x1, x2)
    assert np.allclose(result, x1 + x2)

@given(st.floats(min_value=-1e6, max_value=1e6), st.floats(min_value=-1e6, max_value=1e6))
def test_scalar_output(x1, x2):
    result = np.add(x1, x2)
    assert isinstance(result, float)

@given(st.data())
def test_output_dtype(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    dtype = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float32, np.float64]))
    x1 = data.draw(st.arrays(dtype=dtype, shape=shape))
    x2 = data.draw(st.arrays(dtype=dtype, shape=shape))
    result = np.add(x1, x2)
    assert result.dtype == dtype

@given(st.data())
def test_where_parameter(data):
    shape = data.draw(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))
    x1 = data.draw(st.arrays(dtype=np.float64, shape=shape, elements=st.floats(min_value=-1e6, max_value=1e6)))
    x2 = data.draw(st.arrays(dtype=np.float64, shape=shape, elements=st.floats(min_value=-1e6, max_value=1e6)))
    where = data.draw(st.arrays(dtype=bool, shape=shape))
    result = np.add(x1, x2, where=where)
    expected = np.where(where, x1 + x2, x1)
    assert np.allclose(result, expected)
# End program