from hypothesis import given, strategies as st 
import pandas as pd
import numpy as np
import pandas.api.types as ptypes

@given(
    x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
    bins=st.one_of(
        st.integers(min_value=2),  
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2).map(sorted).filter(lambda l: len(set(l)) > 1),
    ),
    right=st.booleans(),
    labels=st.one_of(st.none(), st.booleans(), st.lists(st.text(), min_size=1)),
    retbins=st.booleans(),
    precision=st.integers(min_value=0),
    include_lowest=st.booleans(),
)
def test_cut(x, bins, right, labels, retbins, precision, include_lowest):
    result = pd.cut(x, bins, right=right, labels=labels, retbins=retbins, precision=precision, include_lowest=include_lowest)

    if retbins:
        assert isinstance(result, tuple) and len(result) == 2
        res, retbins_res = result
        if ptypes.is_integer(bins):
            assert len(retbins_res) == bins
        else:
            assert np.array_equal(np.sort(np.array(retbins_res)), np.sort(np.array(bins)))
