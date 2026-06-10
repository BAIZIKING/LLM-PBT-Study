from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(obj=st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=True),
    st.text(),
    st.lists(st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=True),
        st.text()
    )),
    st.builds(pd.Series, st.lists(st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=True),
        st.text()
    ))),
    st.builds(pd.DataFrame, st.lists(st.lists(st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=True),
        st.text()
    )))),
    st.builds(pd.DatetimeIndex, st.lists(st.one_of(
        st.none(),
        st.datetimes()
    )))
))
def test_pandas_isna_properties(obj):
    result = pd.isna(obj)

    # Property 1: Output should be boolean or array-like of booleans with same shape as input
    assert isinstance(result, (bool, np.ndarray, pd.Series, pd.DataFrame))
    if isinstance(result, np.ndarray):
        assert result.dtype == bool
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        assert result.shape == obj.shape

    # Property 2: If input is scalar, output should be scalar boolean
    if not hasattr(obj, '__len__'):
        assert isinstance(result, bool)

    # Property 3: If any element is NaN, None, or NaT, corresponding output element should be True
    if hasattr(obj, '__len__'):
        for i in range(len(obj)):
            if pd.isna(obj[i]):
                assert result[i]
            else:
                assert not result[i]
    else:
        if pd.isna(obj):
            assert result
        else:
            assert not result

    # Property 4: Function should handle array-like inputs of different data types correctly
    # (tested implicitly by the input strategy)

    # Property 5: For Series and DataFrame inputs, output should be of same type as input
    if isinstance(obj, pd.Series):
        assert isinstance(result, pd.Series)
    if isinstance(obj, pd.DataFrame):
        assert isinstance(result, pd.DataFrame)
# End program