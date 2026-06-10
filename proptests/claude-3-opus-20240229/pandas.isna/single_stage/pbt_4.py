from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Generate a wide variety of input types and edge cases:
# - Scalar types like None, np.nan, pd.NA, strings, ints, floats, bools 
# - Lists, tuples, numpy arrays containing mixtures of those scalars
# - Pandas core types like Series, DataFrame, DatetimeIndex with NAT
# This ensures thorough testing of all supported input types.
@given(x=st.one_of(
    st.none(), 
    st.just(np.nan),
    st.just(pd.NaT), 
    st.booleans(),
    st.text(), 
    st.integers(), 
    st.floats(allow_nan=True),
    st.lists(st.one_of(
        st.none(),
        st.booleans(), 
        st.text(), 
        st.integers(), 
        st.floats(allow_nan=True)
    )),
    st.tuples(st.one_of(
        st.none(),
        st.booleans(), 
        st.text(), 
        st.integers(), 
        st.floats(allow_nan=True)        
    )),
    st.numpy_arrays(st.one_of(
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=True)
    )),
    st.series(
        elements=st.one_of(
            st.booleans(),
            st.integers(),  
            st.text(), 
            st.floats(allow_nan=True)
        ),
        index=st.one_of(
            st.integers(),
            st.text(),
            st.datetimes(),
        )
    ),
    st.data_frames(
        columns=st.integers(1, 5),
        rows=st.integers(1, 10),
        data_columns=st.one_of(
            st.columns(st.booleans()), 
            st.columns(st.text()),
            st.columns(st.floats(allow_nan=True))
        ),
        index=st.one_of(st.integers(), st.datetimes())        
    ),
    st.datetimes(allow_nan=True) | st.timedeltas(allow_nan=True),
))
def test_isna(x):
    result = pd.isna(x)

    # For scalar input, output is a scalar bool
    if np.isscalar(x):
        assert isinstance(result, np.bool_)
    # Otherwise, output type matches input
    else:
        assert type(result) == type(x)

    # Output has same shape/length as input  
    if hasattr(x, 'shape'): 
        assert result.shape == x.shape
    elif hasattr(x, '__len__'):
        assert len(result) == len(x)
    
    # True for missing values, False otherwise
    def is_missing(val):
        return val is None or (isinstance(val, float) and np.isnan(val)) \
            or val is pd.NaT or val is pd.NA

    if not hasattr(x, '__len__'):
        x = [x]
        result = [result]

    for v, r in zip(x, result):
        if is_missing(v):
            assert r
        else:
            assert not r
# End program            