from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for generating various input types
numeric_arrays = st.arrays(np.float64, st.floats(allow_nan=True))
object_arrays = st.arrays(object, st.one_of(st.none(), st.floats(allow_nan=True), st.text()))
datetimelike_arrays = st.arrays(pd.Timestamp, st.datetimes())
scalar_values = st.one_of(st.none(), st.floats(allow_nan=True), st.text(), st.datetimes())
pandas_objects = st.one_of(
    st.dataframes(
        st.lists(st.one_of(numeric_arrays, object_arrays, datetimelike_arrays)),
        st.lists(st.text())  # Column names
    ),
    st.series(st.one_of(numeric_arrays, object_arrays, datetimelike_arrays)),
    st.indexes(st.one_of(st.none(), st.floats(allow_nan=True), st.text(), st.datetimes()))
)

@given(scalar_values)
def test_isna_scalar_output(value):
    """
    Test that pd.isna returns a scalar boolean for scalar inputs.
    """
    result = pd.isna(value)
    assert isinstance(result, bool)
# End program

@given(numeric_arrays)
def test_isna_numeric_array_output(array):
    """
    Test that pd.isna returns an array of booleans with the same shape as the input for numeric arrays.
    """
    result = pd.isna(array)
    assert isinstance(result, np.ndarray)
    assert result.shape == array.shape
    assert result.dtype == bool
# End program

@given(object_arrays)
def test_isna_object_array_output(array):
    """
    Test that pd.isna returns an array of booleans with the same shape as the input for object arrays.
    """
    result = pd.isna(array)
    assert isinstance(result, np.ndarray)
    assert result.shape == array.shape
    assert result.dtype == bool
# End program

@given(datetimelike_arrays)
def test_isna_datetimelike_array_output(array):
    """
    Test that pd.isna returns an array of booleans with the same shape as the input for datetimelike arrays.
    """
    result = pd.isna(array)
    assert isinstance(result, np.ndarray)
    assert result.shape == array.shape
    assert result.dtype == bool
# End program

@given(pandas_objects)
def test_isna_pandas_object_output(obj):
    """
    Test that pd.isna returns the same type as the input for pandas objects.
    """
    result = pd.isna(obj)
    assert type(result) == type(obj)
# End program