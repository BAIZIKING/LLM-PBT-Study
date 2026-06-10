from hypothesis import given, strategies as st
from hypothesis.extra import numpy as np_st
from hypothesis.extra import pandas as pd_st
import pandas as pd
import numpy as np

# Strategy to generate scalar or array-like data
def generate_data(draw):
    strategies = [
        st.just(None),  # Generates None
        st.floats(allow_nan=True),  # Generates float, including nan
        st.text(),  # Generates strings
        pd_st.series(  # Generates pandas series
            elements=st.one_of(st.just(None), st.floats(allow_nan=True), st.text()),
            dtype=st.one_of(st.just(None), st.floats(), st.text()),
            index=pd_st.indexes(elements=st.text())  # Index with random text values
        ),
        pd_st.data_frames([pd_st.column('A', elements=st.one_of(st.just(None), st.floats(allow_nan=True), st.text()))]),  # Generates pandas dataframe
        np_st.arrays(  # Generates numpy array
            dtype=st.one_of(np_st.integer_dtypes(), np_st.float_dtypes(allow_nan=True), np_st.string_dtypes()), 
            shape=st.tuples(st.integers(1, 10), st.integers(1, 10))
        )
    ]
    return draw(st.one_of(strategies))  # Choose one strategy at random


@given(st.data())
def test_pandas_isna(data):
    x = generate_data(data.draw)
    
    result = pd.isna(x)
    
    if np.isscalar(x):
        if pd.isna(x):
            assert result
        else:
            assert not result
    else:
        assert result.shape == x.shape
        if isinstance(x, pd.Series) or isinstance(x, pd.DataFrame):
            assert x.isna().equals(result)
        else:
            assert np.array_equal(pd.isna(x), result)