from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: 
# Generate a wide variety of inputs for x, bins, right, labels, retbins, precision, include_lowest, ordered
# x: 1D array-like of numeric, datetime, or timedelta values. Use arrays, lists, and series with float, int, datetime types.
# bins: int, sequence of scalars, IntervalIndex. Generate ints > 0, lists of unique sorted values, IntervalIndex. 
# right: bool
# labels: array, bool, or None if ordered=True. Use arrays of strings, False, None. Require labels if ordered=False.
# retbins: bool  
# precision: int > 0
# include_lowest: bool
# ordered: bool
# duplicates: 'raise' or 'drop'
# Check properties:
# - Returned bins match input bins (when retbins=True)
# - Number of bins is correct 
# - Bins encompass full range of x
# - Bins are correct type: Interval[float], Interval[int] when x is int, Interval[datetime] when x is datetime, etc.
# - Returned dtype is correct based on labels and x
# - Ordering is correct based on ordered parameter
# - Correct behavior for NA, out of bounds values in x
# - Correct behavior when bins are not unique based on duplicates
@given(st.data())
def test_pd_cut(data):
    x = data.draw(st.one_of(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), 
        st.lists(st.integers(), min_size=1),
        st.lists(st.datetimes(), min_size=1),
        st.lists(st.timedeltas(), min_size=1),
        st.series(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
    ))
    
    bins_strategy = st.one_of(
        st.integers(min_value=1, max_value=len(x)), 
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, unique=True).map(sorted),
        st.lists(st.integers(), min_size=1, unique=True).map(sorted),
        st.lists(st.datetimes(), min_size=1, unique=True).map(sorted),
        st.builds(pd.IntervalIndex.from_breaks, st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True).map(sorted))
    )
    bins = data.draw(bins_strategy)
    
    right = data.draw(st.booleans())
    ordered = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.booleans(), 
                                 st.lists(st.text(), min_size=1, max_size=10)))
    if not ordered:
        assert labels is not None, "labels must be provided when ordered=False"
    retbins = data.draw(st.booleans())
    precision = data.draw(st.integers(min_value=1, max_value=10))
    include_lowest = data.draw(st.booleans())
    duplicates = data.draw(st.sampled_from(['raise', 'drop']))
    
    result = pd.cut(x, bins, right=right, labels=labels, retbins=retbins, precision=precision,
                    include_lowest=include_lowest, ordered=ordered, duplicates=duplicates)
    
    if retbins:
        result, result_bins = result
        if isinstance(bins, int):
            assert np.array_equal(result_bins, np.linspace(min(x), max(x), bins+1))
        elif isinstance(bins, pd.IntervalIndex):
            assert result_bins.equals(bins)
        else:
            assert np.array_equal(result_bins, bins)
    
    if isinstance(bins, int):
        assert result.nunique() == bins
    else:
        assert result.nunique() == len(np.unique(bins))

    assert result.min() <= min(x)
    assert result.max() >= max(x)
    
    if labels is None:
        if isinstance(x, (pd.Series, np.ndarray)) and np.issubdtype(x.dtype, np.integer):
            assert all(isinstance(i, pd.Interval) and i.closed == 'right' for i in result)
        elif isinstance(x, (pd.Series, np.ndarray)) and np.issubdtype(x.dtype, np.datetime64):
            assert all(isinstance(i, pd.Interval) and i.closed == 'right' for i in result)
    
    if isinstance(x, pd.Series):
        assert isinstance(result, pd.Series)
        assert isinstance(result.dtype, pd.CategoricalDtype)
    else:
        assert isinstance(result, pd.Categorical)
    
    if ordered:
        assert result.dtype.ordered
    else:
        assert not result.dtype.ordered
    
    assert pd.isna(result[pd.isna(x)]).all()
        
    if duplicates == 'raise':
        with pd.option_context('mode.chained_assignment', None):
            bins2 = bins.copy()
            bins2[0] = bins[1] 
        with pytest.raises(ValueError):
            pd.cut(x, bins2)
    else:
        with pd.option_context('mode.chained_assignment', None):
            bins2 = bins.copy()
            bins2[0] = bins[1]
        result = pd.cut(x, bins2)
        assert result.nunique() == len(np.unique(bins2))
        
# End program        