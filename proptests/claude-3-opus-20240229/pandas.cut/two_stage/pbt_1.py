from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(x=st.lists(st.floats(allow_nan=True, allow_infinity=False), min_size=1),
       bins=st.one_of(st.integers(2, 100), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100)),
       labels=st.one_of(st.none(), st.lists(st.text(), min_size=1), st.just(False)),
       ordered=st.booleans())
def test_pandas_cut_properties(x, bins, labels, ordered):
    result = pd.cut(x, bins, labels=labels, ordered=ordered)

    # Property 1
    if isinstance(bins, int):
        assert len(result.cat.categories) <= bins
    else:
        assert len(result.cat.categories) <= len(bins) - 1

    # Property 2
    if ordered:
        assert result.cat.ordered
    else:
        assert not result.cat.ordered

    # Property 3
    if isinstance(x, pd.Series):
        assert isinstance(result, pd.Series)
    else:
        assert isinstance(result, pd.Categorical)

    if labels is False:
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int64

    # Property 4
    for value, bin_label in zip(x, result):
        if pd.isna(value):
            assert pd.isna(bin_label)
        else:
            assert bin_label != ''

    # Property 5
    if isinstance(bins, list):
        assert len(bins) == len(set(bins)), "Duplicate bin edges should raise an error"
# End program