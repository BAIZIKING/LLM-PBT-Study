from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.lists(st.text(min_size=1), min_size=1, max_size=5, unique=True),
       st.lists(st.text(min_size=1), min_size=1, max_size=5, unique=True),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5),
       st.sampled_from(['left', 'right', 'outer', 'inner', 'cross'])
      )
def test_pandas_merge(cols1, cols2, values1, values2, how):

    df1 = pd.DataFrame({cols1[i]: [values1[i]] for i in range(len(cols1))})
    df2 = pd.DataFrame({cols2[i]: [values2[i]] for i in range(len(cols2))})

    result = pd.merge(df1, df2, how=how)

    if how != 'inner':
        assert not result.empty

    assert all(col in result.columns for col in cols1 + cols2)

    if how == 'inner':
        assert all(key in result.columns for key in set(cols1).intersection(set(cols2)))