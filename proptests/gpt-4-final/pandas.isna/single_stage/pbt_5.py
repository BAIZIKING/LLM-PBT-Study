from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Generate scalars or array-likes that may contain NaN, None, or NaT
@given(st.one_of(
    st.floats(allow_nan=True),
    st.none(),
    st.lists(st.one_of(st.floats(allow_nan=True), st.none()), max_size=50),
    st.lists(st.datetimes(), min_size=1, max_size=50)
))
def test_pandas_isna(x):
    # Call isna() and store its output
    output = pd.isna(x)
    
    # Property 1: All given scalers return a bool
    if np.isscalar(x):
        assert isinstance(output, (np.bool_, bool)), 'Not bool for scalar'
    
    # Property 2: All given array-likes return a list of bool
    else:
        assert all(isinstance(o, (np.bool_, bool)) for o in output), "Not bool in array-like output"