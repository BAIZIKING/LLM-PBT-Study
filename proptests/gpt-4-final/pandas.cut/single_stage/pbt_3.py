from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.lists(st.integers(), min_size=5), st.integers(min_value=2, max_value=5), st.booleans(), st.one_of(st.none(), st.booleans()), st.booleans(), st.integers(min_value=0, max_value=5), st.booleans(), st.sampled_from(['raise', 'drop']), st.booleans())
def test_pandas_cut(arr, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered):
    arr = pd.Series(arr)
    
    # Check with different strategies for labels
    if labels is None:
        result = pd.cut(arr, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered)
    elif labels:
        labels = ["label"+str(i) for i in range(bins)]
        result = pd.cut(arr, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered)
    else:
        result = pd.cut(arr, bins, right, False, retbins, precision, include_lowest, duplicates, ordered)
    
    if not retbins:
        assert type(result) == pd.Series or type(result) == pd.Categorical
    else:
        assert type(result) == tuple and len(result) == 2