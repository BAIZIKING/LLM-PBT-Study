from hypothesis import given, strategies as st
import numpy as np

@given(
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3))
)
def test_numpy_add_shape(x1, x2):
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3))
)
def test_numpy_add_element_wise(x1, x2):
    result = np.add(x1, x2)
    assert np.array_equal(result, x1 + x2)

@given(st.floats(allow_infinity=False, allow_nan=False), st.floats(allow_infinity=False, allow_nan=False))
def test_numpy_add_scalars(x1, x2):
    result = np.add(x1, x2)
    assert isinstance(result, np.float64) and result == x1 + x2

@given(
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.arrays(np.float64, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.arrays(np.bool_, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3))
)
def test_numpy_add_where(x1, x2, where):
    result = np.add(x1, x2, where=where)
    expected = np.where(where, x1 + x2, x1)
    assert np.array_equal(result, expected)

@given(
    st.arrays(np.int8, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.arrays(np.int16, shape=st.tuples(*[st.integers(min_value=0, max_value=10)] * 3)),
    st.sampled_from([None, np.float64])
)
def test_numpy_add_dtype(x1, x2, dtype):
    result = np.add(x1, x2, dtype=dtype)
    if dtype is None:
        assert result.dtype == np.result_type(x1, x2)
    else:
        assert result.dtype == dtype
# End program