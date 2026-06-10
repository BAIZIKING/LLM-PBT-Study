from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a wide variety of input types including scalar values (integers, floats, strings, None, booleans),
# numpy arrays with different dimensions and dtypes, pandas Series with various dtypes, and pandas DataFrames.
# Properties to test:
# 1. Output type is always boolean for scalar input or matching array of booleans for array-like input 
# 2. Output indicates missing values correctly (e.g. NaN, None, NaT)
# 3. Handles all valid input types as documented
@given(st.one_of(
    st.none(), 
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=True),
    st.text(),
    st.dates(),
    st.arrays(
        st.one_of(
            st.none(),
            st.booleans(),  
            st.integers(),
            st.floats(allow_nan=True),
            st.text(),
            st.dates()
        ), 
        min_dims=1,
        max_dims=5
    ).map(np.array),
    st.lists(
        st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=True), 
            st.text(),
            st.dates()
        )
    ).map(pd.Series),
    st.lists(
        st.lists(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=True),
                st.text(), 
                st.dates()
            )
        )
    ).map(pd.DataFrame)
))
def test_isna(obj):
    result = pd.isna(obj)
    
    if np.isscalar(obj):
        assert isinstance(result, bool)
    else:
        assert result.shape == np.array(obj).shape
        assert result.dtype == bool
        
    if isinstance(obj, float):
        assert result == np.isnan(obj)
    elif obj is None or obj is pd.NaT:
        assert result == True
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        expected = obj.apply(pd.isna)
        pd.testing.assert_series_equal(result, expected)
# End program