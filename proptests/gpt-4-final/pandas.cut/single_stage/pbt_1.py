from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    x=st.lists(st.integers(), min_size=2),
    bins=st.integers(min_value=2),
    right=st.booleans(),
    labels=st.one_of(st.none(), st.lists(st.text(), min_size=2), st.just(False)),
    retbins=st.booleans(),
    precision=st.integers(min_value=0, max_value=10),
    include_lowest=st.booleans(),
    duplicates=st.sampled_from(['raise', 'drop']),
    ordered=st.booleans()
)
def test_pandas_cut(x, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered):
    if isinstance(labels, list) and len(labels) != bins:
        labels = labels[:bins]
    result = pd.cut(x, bins, right=right, labels=labels, retbins=retbins, precision=precision, include_lowest=include_lowest, duplicates=duplicates, ordered=ordered)
    if(isinstance(result,pd.core.series.Series)):
        assert len(result) == len(x)
    elif(isinstance(result, np.ndarray)):
        assert len(result) == bins

    if labels == False:
        assert isinstance(result, np.ndarray)
    if retbins:
        assert isinstance(result[1], np.ndarray)
    return result