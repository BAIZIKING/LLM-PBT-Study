from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers(), min_size=1, max_size=5), st.lists(st.integers(), min_size=1, max_size=5))
def test_add_shape_property(list1, list2):
    arr1 = np.array(list1)
    arr2 = np.array(list2)
    result = np.add(arr1, arr2)
    assert result.shape == np.broadcast(arr1, arr2).shape

@given(st.integers(), st.floats())
def test_add_dtype_property(x, y):
    result = np.add(x, y)
    assert isinstance(result, np.float64)

@given(st.lists(st.integers(), min_size=1, max_size=5), st.lists(st.integers(), min_size=1, max_size=5))
def test_add_out_property(list1, list2):
    arr1 = np.array(list1)
    arr2 = np.array(list2)
    out = np.empty_like(arr1)
    id_before = id(out)
    np.add(arr1, arr2, out=out)
    id_after = id(out)
    assert id_before == id_after

@given(st.integers(), st.integers())
def test_add_scalar_input_property(a, b):
    result = np.add(a, b)
    assert np.isscalar(result)

@given(st.lists(st.bools(), min_size=1, max_size=5), st.just([True, False]))
def test_add_where_property(list1, where_condition):
    arr1 = np.array(list1)
    arr2 = np.array(list1)
    out = np.zeros_like(arr1)
    np.add(arr1, arr2, out=out, where=where_condition)
    assert (out[where_condition] == arr1 + arr2)[where_condition]
    assert (out[~where_condition] == 0)[~where_condition]
# End program