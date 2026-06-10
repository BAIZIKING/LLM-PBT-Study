from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a wide variety of scalar and array-like inputs to test pandas.isna.
# Include common types like int, float, str, bool, datetime, None, np.nan, and pd.NA. 
# Also generate arrays, Series, DataFrames, and Index objects containing mixtures
# of these types and missing values. Verify the output type and values match 
# the expected behavior from the documentation.
@given(st.one_of(
    st.none(), 
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=True),
    st.text(),
    st.datetimes(),
    st.just(pd.NA),
    st.just(np.nan),
    st.lists(st.one_of(
        st.none(),
        st.booleans(), 
        st.integers(), 
        st.floats(allow_nan=True),
        st.text(),
        st.datetimes(),
        st.just(pd.NA),
        st.just(np.nan)
    )),
    st.series(
        st.one_of(
            st.booleans(), 
            st.integers(), 
            st.floats(allow_nan=True),
            st.text(),
            st.datetimes(),
            st.just(pd.NA) 
        )
    ),
    st.data_frames(
        columns=st.just(["A", "B"]),
        rows=st.lists(
            st.lists(
                st.one_of(
                    st.booleans(),
                    st.integers(),
                    st.floats(allow_nan=True), 
                    st.text(),
                    st.datetimes(),
                    st.none(),
                    st.just(pd.NA)
                ),
                min_size=2,
                max_size=2
            ),
            min_size=2
        )
    ),
    st.datetimes(),
    st.dates()
))
def test_isna(obj):
    result = pd.isna(obj)
    
    if np.isscalar(obj):
        assert isinstance(result, bool)
    else:
        assert result.shape == np.asarray(obj).shape
        
    if isinstance(obj, pd.Series):
        assert isinstance(result, pd.Series)
    elif isinstance(obj, pd.DataFrame):
        assert isinstance(result, pd.DataFrame)
    elif isinstance(obj, pd.DatetimeIndex):
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
    else:
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        
    missing_values = [None, np.nan, pd.NA, pd.NaT]
    
    if any(pd.isna(x) for x in np.asarray(obj).ravel() if x in missing_values):
        assert result.any()
    else:
        assert not result.any()
# End program