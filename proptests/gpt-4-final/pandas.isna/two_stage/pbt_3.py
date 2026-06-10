from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.one_of(st.text(), st.floats(allow_nan=False), st.dates()))
def test_pandas_isna_scalar_objects(input_obj):
    assert pd.isna(input_obj) == False

@given(st.lists(st.floats(allow_nan=True), min_size=1))
def test_pandas_isna_nonempty_float_lists(input_list):
    nan_in_list = any(pd.isna(element) for element in input_list)
    output_list = pd.isna(input_list)
    assert (nan_in_list == True) == (any(output_list))

@given(st.lists(st.floats(allow_nan=False), min_size=1))
def test_pandas_isna_nonempty_float_lists_without_nan(input_list):
    output_list = pd.isna(input_list)
    assert not any(output_list)

@given(st.data())
def test_pandas_isna_array_numpy(data):
    numpy_array = np.array(data.draw(
        st.lists(st.lists(st.floats(allow_nan=True), min_size=1, max_size=5), min_size=1, max_size=5)), 
        dtype=object)
    output_array = pd.isna(numpy_array)
    assert numpy_array.shape == output_array.shape

@given(st.data())
def test_pandas_isna_dataframe(data):
    nrows, ncols = data.draw(st.integers(min_value=1, max_value=10)), data.draw(st.integers(min_value=1, max_value=10))
    dataframe = pd.DataFrame(data=data.draw(
        st.lists(st.lists(st.floats(allow_nan=True), min_size=ncols, max_size=ncols),
        min_size=nrows, max_size=nrows)))
    output_dataframe = pd.isna(dataframe)
    assert output_dataframe.shape == dataframe.shape
    assert type(output_dataframe) == type(dataframe)