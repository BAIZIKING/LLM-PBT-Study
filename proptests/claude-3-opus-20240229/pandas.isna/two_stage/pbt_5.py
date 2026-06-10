from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

@given(st.data())
def test_pandas_isna_output_type(data):
    obj = data.draw(st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=True),
        st.text(),
        st.lists(st.one_of(st.none(), st.booleans(), st.floats(allow_nan=True), st.text())),
        st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.floats(allow_nan=True)),
        st.arrays(object, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.one_of(st.none(), st.booleans(), st.floats(allow_nan=True), st.text()))
    ))
    result = pd.isna(obj)
    assert isinstance(result, (bool, np.ndarray))
    if isinstance(obj, (list, np.ndarray)):
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
    else:
        assert isinstance(result, bool)

@given(st.data())
def test_pandas_isna_output_shape(data):
    obj = data.draw(st.one_of(
        st.lists(st.one_of(st.none(), st.booleans(), st.floats(allow_nan=True), st.text())),
        st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.floats(allow_nan=True)),
        st.arrays(object, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.one_of(st.none(), st.booleans(), st.floats(allow_nan=True), st.text()))
    ))
    result = pd.isna(obj)
    assert result.shape == np.array(obj).shape

@given(st.data())
def test_pandas_isna_numeric_arrays(data):
    arr = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.floats(allow_nan=True)))
    result = pd.isna(arr)
    assert result.dtype == bool
    assert np.array_equal(result, np.isnan(arr))

@given(st.data())
def test_pandas_isna_object_arrays(data):
    arr = data.draw(st.arrays(object, shape=st.tuples(st.integers(min_value=0, max_value=10)), fill=st.one_of(st.none(), st.booleans(), st.floats(allow_nan=True), st.text())))
    result = pd.isna(arr)
    assert result.dtype == bool
    expected = np.array([pd.isna(x) for x in arr.flatten()]).reshape(arr.shape)
    assert np.array_equal(result, expected)
# End program