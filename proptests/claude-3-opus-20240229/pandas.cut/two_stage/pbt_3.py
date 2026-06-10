from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(x=st.one_of(st.lists(st.integers()), st.lists(st.floats())), 
       bins=st.one_of(st.integers(1, 100), st.lists(st.floats(), min_size=1, max_size=100)),
       labels=st.one_of(st.none(), st.lists(st.text(), min_size=1, max_size=100), st.just(False)),
       ordered=st.booleans())
def test_pandas_cut_properties(x, bins, labels, ordered):
    # Property 1: Number of unique bins should match the specified bins
    if isinstance(bins, int):
        assert pd.cut(x, bins).nunique() == bins
    elif isinstance(bins, list):
        assert pd.cut(x, bins).nunique() == len(set(bins)) - 1
    
    # Property 2: Output container type should be categorical, series, or ndarray
    if isinstance(x, pd.Series):
        assert isinstance(pd.cut(x, bins), pd.Series)
    else:
        if labels is None or isinstance(labels, list):
            assert isinstance(pd.cut(x, bins, labels=labels), pd.Categorical)
        elif labels is False:
            assert isinstance(pd.cut(x, bins, labels=labels), np.ndarray)
    
    # Property 3: Output index should match input index for series
    if isinstance(x, pd.Series):
        assert pd.cut(x, bins).index.equals(x.index)
    
    # Property 4: All values should be binned, and each value should fall into exactly one bin
    result = pd.cut(x, bins)
    assert result.notna().sum() <= len(x)
    assert len(result) == len(x)
    
    # Property 5: Resulting bins should be ordered or unordered based on the `ordered` parameter
    assert pd.cut(x, bins, ordered=ordered).ordered == ordered

# End program