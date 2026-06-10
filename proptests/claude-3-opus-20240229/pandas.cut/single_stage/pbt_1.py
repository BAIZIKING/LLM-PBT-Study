from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: 
# Generate a wide variety of inputs for pandas.cut, including:
# - 1D array-like input x of various lengths and element types
# - Bins specified as an int, 1D sequence of scalars, and IntervalIndex 
# - right, labels, include_lowest, ordered parameters
# - Edge cases: empty/single element x, bins out of range of x, non-unique bins
# Check the following properties:
# - Output is a Series, Categorical or ndarray with same length as x
# - Bins are left-closed, right-open intervals unless include_lowest=True
# - Intervals are ordered if ordered=True, unordered if ordered=False  
# - Labels match the number of bins if specified
# - Out of range x values are assigned NaN
@given(x=st.one_of(st.lists(st.integers()), st.lists(st.floats(allow_nan=False, allow_infinity=False))),
       bins=st.one_of(st.integers(1, 100), 
                      st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100).map(sorted),
                      st.builds(pd.IntervalIndex.from_breaks, st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100, unique=True))),
       right=st.booleans(),
       labels=st.one_of(st.none(), st.booleans(), st.lists(st.text(), min_size=1)),
       include_lowest=st.booleans(),
       ordered=st.booleans())
def test_pandas_cut(x, bins, right, labels, include_lowest, ordered):
    x = np.array(x) 
    
    if isinstance(labels, list) and isinstance(bins, int):
        assume(len(labels) == bins)
    if isinstance(labels, list) and isinstance(bins, list):
        assume(len(labels) == len(bins)-1)
        
    if isinstance(bins, int):
        assume(bins > 0)
    else:
        assume(len(bins) > 0)
        
    if isinstance(bins, pd.IntervalIndex):
        assume(right == True)
        assume(ordered == True)
        
    if not ordered:
        assume(isinstance(labels, list))
        
    if labels == True:
        reject()

    out = pd.cut(x, bins, right, labels, retbins=False, include_lowest=include_lowest, ordered=ordered)
    
    assert len(out) == len(x)
    assert isinstance(out, (pd.Series, pd.Categorical, np.ndarray))
    
    if isinstance(out, pd.Series):
        assert isinstance(out.dtype, pd.CategoricalDtype)
        cats = out.dtype.categories
    elif isinstance(out, pd.Categorical):
        cats = out.categories
    else:
        cats = None
        
    if cats is not None:
        if ordered:
            assert isinstance(cats, pd.IntervalIndex) and cats.is_monotonic_increasing
        else:
            assert isinstance(cats, pd.IntervalIndex)
            
        if isinstance(bins, pd.IntervalIndex):
            assert cats.equals(bins)
        else:
            assert (len(cats)+1 == bins) if isinstance(bins, int) else (len(cats)+1 == len(bins))
        
        for interval in cats:
            assert interval.closed_left == (not right or include_lowest)
            assert interval.open_right == right
        
        if isinstance(labels, list):
            assert len(cats) == len(labels)
            assert all(a == b for a,b in zip(cats.astype(str), labels)) 
            
        oob_mask = (x < cats[0].left) | (x > cats[-1].right)
        assert all(xi == np.nan for (xi, oob) in zip(out, oob_mask) if oob)
        
# End program        