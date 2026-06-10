from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a wide variety of input types and edge cases for pandas.cut:
# - Generate 1D array-like inputs of various types (list, numpy array, pandas Series)  
# - Generate bins as an int, sequence of scalars, and IntervalIndex
# - Generate edge cases like empty input, NaNs, +/- inf, out of bounds values
# - Vary other parameters like right, labels, precision, include_lowest
# Properties to test based on documentation:
# - Output type should be Categorical, Series, or ndarray depending on input
# - Number of output bins should match input bins (accounting for out of bounds values) 
# - Bins should cover full range of input x (plus small % if bins is an int)
# - Right/left bin edges are inclusive/exclusive based on right parameter
# - First bin is left-inclusive if include_lowest=True  
# - Labels are used properly for bins if provided
# - Precision applies to display of bin labels
# - Out of bounds values and NaNs should be NA in output
@given(st.data())
def test_cut(data):
    
    # Generate input data x
    x = data.draw(st.one_of(
        st.lists(st.floats(allow_infinity=True, allow_nan=True), min_size=0, max_size=100),
        st.arrays(float, 0, 100),
        st.series(st.floats(allow_infinity=True, allow_nan=True), dtype=float)
    ))
    
    # Generate bins
    bins = data.draw(st.one_of(
        st.integers(1, 10), 
        st.lists(st.floats(allow_infinity=True), min_size=1, max_size=10),
        st.builds(pd.IntervalIndex.from_breaks, st.lists(st.floats(), min_size=2, max_size=10, unique=True))
    ))
    
    # Generate other parameters
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans()) 
    precision = data.draw(st.integers(1, 5))
    labels = data.draw(st.one_of(st.none(), st.booleans(), 
                                 st.lists(st.text(), min_size=1, max_size=10)))
    
    # Call function
    if labels is not None and len(labels) not in (0, 1, 10):
        labels = None # avoid invalid labels
    result = pd.cut(x, bins, right=right, labels=labels, 
                    precision=precision, include_lowest=include_lowest)
    
    # Check output type
    if isinstance(x, pd.Series):
        assert isinstance(result, pd.Series)
    elif labels is False:
        assert isinstance(result, np.ndarray) and result.dtype == int
    else:
        assert isinstance(result, pd.Categorical)
        
    # Check number of bins
    if isinstance(bins, int):
        assert len(result.categories) == bins
    else:
        assert len(result.categories) <= len(bins) - 1
    
    # Check binning    
    if len(x) > 0:
        if isinstance(bins, int): # adjust edges by .1%
            xmin, xmax = np.min(x), np.max(x)
            rng = xmax - xmin
            bins = np.linspace(xmin - rng*.001, xmax + rng*.001, bins+1)
        elif not isinstance(bins, pd.IntervalIndex):
            bins = pd.IntervalIndex.from_breaks(bins)
        
        for i in range(1, len(result.categories)):
            prev = result.categories[i-1]
            curr = result.categories[i]
            assert prev.right < curr.left  
        
        # Check right/include_lowest
        if isinstance(x, pd.Series):
            x = x.values
        for a, b in zip(x, result):
            if not np.isnan(a):
                assert b.left < a <= b.right if right else b.left <= a < b.right
                if include_lowest and a == bins[0]:
                    assert a == b.left
        
    # Check labels and precision
    if labels is None or labels is False:
        for b in result.categories:
            assert str(b) == str(b.left) + ', ' + str(b.right) + ']'  
    else:
        assert len(labels) == len(result.categories)
        assert list(result.categories) == [f'({a:.{precision}f}, {b:.{precision}f}]' for a,b in zip(bins[:-1], bins[1:])]

    # Check NA handling
    if isinstance(x, pd.Series):
        assert result.isna().equals(x.isna())  
    else:
        assert np.isnan(result[np.isnan(x)]).all()
        
    if not isinstance(bins, pd.IntervalIndex):    
        oob = (x < bins[0]) | (x > bins[-1])
        assert np.isnan(result[oob]).all()
        assert not np.isnan(result[~oob]).any()
        
# End program