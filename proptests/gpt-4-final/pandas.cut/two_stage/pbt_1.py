from hypothesis import given, strategies as st
import numpy as np
import pandas as pd


@given(
    x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
    bins=st.one_of(st.integers(min_value=2), st.lists(st.floats(min_value=-100, max_value=100), min_size=2, unique=True)),
    right=st.booleans(),
    labels=st.one_of(st.none(), st.booleans(), st.lists(st.text(), min_size=1)),
    retbins=st.booleans(),
    precision=st.integers(min_value=0),
    include_lowest=st.booleans(),
    duplicates=st.sampled_from(['raise', 'drop']),
    ordered=st.booleans()
)
def test_pandas_cut_property(x, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered):
    if isinstance(bins, list) and len(set(np.diff(np.sort(bins)))) != 1 and len(bins) <= 1:
        return
    precision = min(15, precision)  # pandas.cut has precision issue beyond 15
    try:
        result = pd.cut(x, bins, right=right, labels=labels, retbins=retbins,
                        precision=precision, include_lowest=include_lowest,
                        duplicates=duplicates, ordered=ordered)
    except ValueError:
        # Ignore tests that would raise errors by design (e.g., duplicate edges with duplicates='raise')
        return  

    # Now check properties
    if labels is False:
        assert all(isinstance(i, np.integer) for i in result)
    elif labels is None or isinstance(labels, list):
        if isinstance(result, pd.Series):
            assert pd.api.types.is_categorical_dtype(result)
        elif isinstance(result, tuple) and not retbins:
            response, bins = result
            assert pd.api.types.is_categorical_dtype(response)
    if retbins:
        if isinstance(bins, int):  # calculated bins
            assert isinstance(result[1], np.ndarray)
        else:  # specified bins
            assert isinstance(result[1], (np.ndarray, pd.IntervalIndex))
# End program