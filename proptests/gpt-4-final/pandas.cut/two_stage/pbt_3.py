from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    st.lists(st.integers(-100, 100)),
    st.integers(1, 10),
    st.booleans(),
    st.one_of(st.none(), st.booleans(), st.lists(st.text())),
    st.booleans(),
    st.integers(1, 5),
    st.booleans(),
    st.sampled_from(["raise", "drop"]),
    st.booleans()
)
def test_pandas_cut_property(x, bins, right, labels, retbins, precision, include_lowest, duplicates, ordered):
    result, bins_result = pd.cut(x, bins, right=right, labels=labels, retbins=retbins, 
                                 precision=precision, include_lowest=include_lowest, 
                                 duplicates=duplicates, ordered=ordered)

    # Test 1: Output type matches the expected type
    if labels is False:
        assert isinstance(result, np.ndarray)
    else:
        if isinstance(x, pd.Series):
            assert isinstance(result, pd.Series)
        else:
            assert isinstance(result, pd.Categorical)

    # Test 2: Number of bins match
    assert len(pd.unique(bins_result)) == bins

    # Test 3: Order of labels
    if ordered:
        assert all(result[i] <= result[i+1] for i in range(len(result)-1))

    # Test 4: First interval inclusion
    if include_lowest:
        assert bins_result[0] == min(x)
    else:
        assert bins_result[0] < min(x)

    # Test 5: Bin return condition
    if retbins:
        assert isinstance(bins_result, np.ndarray)
    else:
        assert bins_result is None

# End program