from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: This strategy aims to generate a wide variety of inputs for the pandas.isna function, including scalars, lists, NumPy arrays, pandas Series, and pandas DataFrames. It considers different data types like integers, floats, strings, datetimes, and None to cover edge cases and ensure comprehensive testing.

@given(st.data())
def test_pandas_isna(data):
    # Generate scalars
    scalar_int = data.draw(st.integers())
    scalar_float = data.draw(st.floats(allow_nan=True))
    scalar_str = data.draw(st.text())
    scalar_datetime = data.draw(st.datetimes())
    scalar_none = None

    # Generate lists and NumPy arrays
    list_data = data.draw(st.lists(st.one_of(st.integers(), st.floats(allow_nan=True), st.none())))
    array_data = data.draw(st.arrays(dtype=np.float64, elements=st.floats(allow_nan=True), shape=st.tuples(st.integers(min_value=1), st.integers(min_value=1))))

    # Generate pandas Series and DataFrames
    series_data = data.draw(st.series(st.one_of(st.integers(), st.floats(allow_nan=True), st.none())))
    df_data = data.draw(st.data_frames(columns=st.column_names(), rows=st.lists(st.one_of(st.integers(), st.floats(allow_nan=True), st.none()))))

    # Test scalar inputs
    assert pd.isna(scalar_int) == False
    assert pd.isna(scalar_float) == np.isnan(scalar_float)
    assert pd.isna(scalar_str) == False
    assert pd.isna(scalar_datetime) == False
    assert pd.isna(scalar_none) == True

    # Test list and NumPy array inputs
    assert all(pd.isna(list_data) == [x is None for x in list_data])
    assert np.array_equal(pd.isna(array_data), np.isnan(array_data))

    # Test pandas Series and DataFrame inputs
    assert all(pd.isna(series_data) == series_data.isna())
    assert pd.isna(df_data).equals(df_data.isna())

# End program