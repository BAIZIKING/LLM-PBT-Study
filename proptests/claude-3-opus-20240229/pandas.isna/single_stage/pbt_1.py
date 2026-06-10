from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a variety of input types including scalar values (None, NaN, NaT, strings, numbers),
# numpy arrays (containing a mix of valid and missing values), pandas Series and DataFrames.
# Properties to test include:
# 1. Output is always bool for scalar input or array of bools for array-like input
# 2. True is returned for missing values (None, NaN, NaT), False for non-missing 
# 3. Shape and type of output matches shape and type of input
@given(st.one_of(
    st.none(), 
    st.floats(allow_nan=True), 
    st.datetimes(allow_nan=True),
    st.text(),
    st.integers(),
    st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.integers()), min_size=1).map(np.array),
    st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.text()), min_size=1).map(pd.Series),
    st.lists(st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.text()), min_size=1), min_size=1).map(pd.DataFrame)
))
def test_isna(obj):
    result = pd.isna(obj)
    if np.isscalar(obj):
        assert isinstance(result, bool)
        assert result == (obj is None or np.isnan(obj) or isinstance(obj, float) and np.isnan(obj) or pd.isna(obj))
    else:
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == np.asarray(obj).shape
        assert (result == [pd.isna(x) for x in np.asarray(obj).flat]).all()
        
# End program