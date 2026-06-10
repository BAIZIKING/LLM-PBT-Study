from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate a wide variety of input data for x, bins, and other parameters.
# - Generate x as a numpy array of floats or ints
# - Generate bins as an integer, array of unique values, or an IntervalIndex
# - Randomly select other parameter values that fit the API constraints
# - Include edge cases like empty arrays, arrays with NaNs or Infs, bins with duplicates or unsorted values
# Properties to test:
# - Output is a Series, ndarray or Categorical with correct shape
# - Bins are in ascending order and include x's min/max values 
# - Right=True/False and include_lowest arguments are respected
# - Passing labels=False returns integer codes
# - Passing ordered=True/False returns an ordered/unordered Categorical
# - Out of bounds values are assigned NaN
@given(st.data())
def test_pandas_cut(data):
    x = data.draw(st.one_of(
        st.arrays(st.floats(allow_nan=True, allow_infinity=True), shape=st.integers(0, 100)),
        st.arrays(st.integers(), shape=st.integers(0, 100))
    ))
    bins_strategy = st.one_of(
        st.integers(1, 10), 
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10).map(sorted).filter(lambda x: len(set(x)) == len(x)),
        st.builds(pd.IntervalIndex.from_breaks, st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10, unique=True))
    )
    bins = data.draw(bins_strategy)
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    ordered = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.booleans()))
    if isinstance(labels, bool) and labels:
        labels = data.draw(st.lists(st.text(), min_size=1, max_size=10))
    
    result = pd.cut(x, bins, right=right, labels=labels, include_lowest=include_lowest, ordered=ordered)

    if labels is None or isinstance(labels, list):
        assert isinstance(result, (pd.Series, pd.Categorical))
    else:
        assert isinstance(result, np.ndarray) and result.dtype == np.int64
    
    assert len(result) == len(x)
    
    if isinstance(bins, int):
        assert len(result.categories) == bins
    else:
        if isinstance(bins, pd.IntervalIndex):
            assert result.categories.equals(bins)
        else:
            assert np.array_equal(result.categories.left, bins[:-1]) 
            assert np.array_equal(result.categories.right, bins[1:])

    assert pd.isnull(result[pd.isnull(x).squeeze()]).all()
    assert pd.isnull(result[np.array([(a < bins[0] or a > bins[-1]) for a in x])]).all()

    assert result.categories.is_monotonic_increasing
    assert (result.categories.left[1:] >= result.categories.right[:-1]).all()
    assert (result.categories.right <= bins[-1]).all() if right else (result.categories.right < bins[-1]).all()
    assert result.categories[0].left <= bins[0] if include_lowest else result.categories[0].left < bins[0]

    if ordered:
        assert result.ordered
    else:
        assert not result.ordered
# End program