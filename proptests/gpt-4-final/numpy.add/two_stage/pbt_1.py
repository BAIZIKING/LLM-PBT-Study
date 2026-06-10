from hypothesis import given, strategies as st
import numpy as np
import numpy.testing as npt

# Property 1: The shape of the output array is the same as the common broadcasted shape of the input arrays
@given(st.lists(st.integers(), min_size=1, max_size=3))
def test_add_shape_property(shape):
    # Generate input arrays that are broadcastable to the given shape
    x1 = np.ones(shape)
    x2 = np.ones(shape)
    result = np.add(x1, x2)
    assert result.shape == x1.shape

# Property 2: The dtype of the output array is compatible with the dtypes of the input arrays
@given(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
def test_add_dtype_property(dtype):
    x1 = np.ones(10, dtype=dtype)
    x2 = np.ones(10, dtype=dtype)
    result = np.add(x1, x2)
    assert result.dtype == x1.dtype

# Property 3: If 'out' argument is used, the function stores the results in the provided 'out' array
@given(st.lists(st.integers(), min_size=1, max_size=3))
def test_add_out_property(shape):
    x1 = np.ones(shape)
    x2 = np.ones(shape)
    out = np.zeros(shape)
    id_before = id(out)
    np.add(x1, x2, out=out)
    assert id_before == id(out)

# Property 4: If 'where' argument is provided, the result in 'out' array should be set to the ufunc result only
# at the locations where the condition is True
@given(st.lists(st.integers(), min_size=1, max_size=3))
def test_add_where_property(list_length):
    x1 = np.ones(list_length)
    x2 = np.ones(list_length)
    where = np.zeros(list_length, dtype=bool)
    out = np.zeros(list_length)
    np.add(x1, x2, out=out, where=where)
    npt.assert_array_equal(out, np.zeros(list_length))

# Property 5: The result of the numpy.add function should match the result of the equivalent Python operation x1 + x2
@given(st.lists(st.integers(), min_size=1, max_size=3))
def test_add_python_equivalent_property(list_length):
    x1 = np.arange(list_length)
    x2 = np.arange(list_length)
    result = np.add(x1, x2)
    npt.assert_array_equal(result, x1 + x2)