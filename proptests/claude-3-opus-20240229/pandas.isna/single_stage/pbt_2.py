from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate a variety of input types including:
# - Scalar values like None, NaN, NaT, integers, floats, strings, booleans 
# - Numpy arrays containing a mix of valid values and NaN
# - Pandas Series containing a mix of valid values and NaN/None
# - Pandas DataFrame containing a mix of valid values and NaN/None
# - Pandas DatetimeIndex containing a mix of valid values and NaT
# Properties to test:
# - Output is always bool for scalar input
# - Output is always same shape ndarray of bool for array-like input
# - True is returned for missing values like NaN, None, NaT
# - False is returned for non-missing values  
@given(st.one_of(
    st.none(), 
    st.floats(allow_nan=True),
    st.datetimes(allow_nat=True),
    st.booleans(),
    st.text(),
    st.integers(),
    st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.integers(), st.booleans(), st.text()), min_size=1).map(np.array),
    st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.integers(), st.booleans(), st.text()), min_size=1).map(pd.Series),
    st.lists(st.lists(st.one_of(st.none(), st.floats(allow_nan=True), st.integers(), st.booleans(), st.text()), min_size=1), min_size=1).map(pd.DataFrame),
    st.lists(st.one_of(st.none(), st.datetimes(allow_nat=True), st.integers(), st.floats()), min_size=1).map(pd.DatetimeIndex)
))
def test_isna(obj):
    result = pd.isna(obj)
    if np.isscalar(obj):
        assert isinstance(result, bool)
    else:
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == np.array(obj).shape
        
    missing_values = [pd.NA, pd.NaT, None, np.nan]
    for x in np.array(obj).flatten():
        if x in missing_values:
            assert pd.isna(x)
        else:
            assert not pd.isna(x)
# End program            