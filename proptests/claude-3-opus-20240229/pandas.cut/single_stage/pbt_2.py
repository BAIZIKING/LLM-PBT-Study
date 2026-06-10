from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Generate a variety of input data for x:
# - Scalar numpy arrays with float and int dtypes 
# - Pandas Series with float/int dtypes and ordered/unordered index
# - Empty and single element arrays/Series 
# - Arrays/Series with NaN and +/- inf values
#
# For bins, labels, include_lowest, right, precision parameters,  
# generate both valid and invalid values to test error handling.
#
# Check the following properties:
# - Output has correct type based on labels (ndarray, Categorical, Series)
# - Number of bins matches expected 
# - Bins are monotonically increasing, non-overlapping intervals
# - Right endpoint of bins is inclusive or not based on `right` param
# - Precision of bin labels matches `precision` argument
# - `include_lowest` is respected for first bin
# - Out of bound and NA values in x are mapped to NA 
# - Passing IntervalIndex for `bins` returns those exact bins
# - Ordering of categorical output based on `ordered`
#
@given(st.data())
def test_pandas_cut(data):
    x = data.draw(st.one_of(
        st.arrays(st.floats(allow_infinity=True, allow_nan=True), shape=st.integers(0, 100)),
        st.arrays(st.integers(), shape=st.integers(0, 100)), 
        st.series(elements=st.floats(allow_infinity=True, allow_nan=True),
                  index=st.one_of(st.none(), st.lists(st.floats())), dtype=float), 
        st.series(elements=st.integers(),
                  index=st.one_of(st.none(), st.lists(st.floats())), dtype=int)
    ))
    
    bins = data.draw(st.one_of(
        st.integers(2, 10),
        st.lists(st.floats(allow_infinity=True, allow_nan=True), min_size=1, max_size=10).map(np.array),
        st.builds(pd.IntervalIndex.from_tuples, st.lists(st.tuples(st.integers(), st.integers()), unique=True, min_size=1, max_size=10))
    ))

    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans()) 
    precision = data.draw(st.integers(1, 5))

    labels = data.draw(st.one_of(
        st.none(), st.booleans(),
        st.lists(elements=st.integers(), min_size=1, max_size=10), 
        st.lists(elements=st.text(), min_size=1, max_size=10)
    ))
    
    ordered = data.draw(st.booleans())
    
    result = pd.cut(x, bins, right=right, labels=labels, include_lowest=include_lowest, 
                    precision=precision, ordered=ordered)
    
    assert isinstance(result, (np.ndarray, pd.Categorical, pd.Series))
    
    if labels is None or isinstance(labels, list):
        assert isinstance(result, (pd.Series, pd.Categorical))
    elif labels is False:
        assert isinstance(result, np.ndarray)
        assert result.dtype == int
    
    if isinstance(bins, int):
        assert len(result.categories) == bins
    elif isinstance(bins, np.ndarray):  
        assert len(result.categories) == len(bins) - 1
    elif isinstance(bins, pd.IntervalIndex):
        assert result.categories.equals(bins)
        
    assert result.categories.is_monotonic_increasing
    assert not result.categories.overlaps
    
    assert result.categories.closed == 'right' if right else 'left'
    assert len(str(result.categories[0].right)) == precision + 2
    
    if include_lowest:
        assert result.categories[0].left == result.categories[0].right
    
    assert pd.isna(result[pd.isna(x)]).all()
    
    if isinstance(x, (pd.Series, np.ndarray)):
        outbound = (x < result.categories[0].left) | (x > result.categories[-1].right)
        assert pd.isna(result[outbound]).all()
        
    assert result.ordered == ordered

# End program