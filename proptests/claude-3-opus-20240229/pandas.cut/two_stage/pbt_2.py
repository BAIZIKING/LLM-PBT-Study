from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), bins=st.integers(2, 100), right=st.booleans(), include_lowest=st.booleans(), ordered=st.booleans())
def test_pandas_cut_length(x, bins, right, include_lowest, ordered):
    result = pd.cut(x, bins, right=right, include_lowest=include_lowest, ordered=ordered)
    assert len(result) == len(x)

@given(x=st.one_of(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.series(st.floats(allow_nan=False, allow_infinity=False), index=st.one_of(st.text(), st.none())), st.arrays(np.float64, st.integers(1, 100))), bins=st.integers(2, 100), labels=st.one_of(st.none(), st.booleans()))
def test_pandas_cut_output_type(x, bins, labels):
    result = pd.cut(x, bins, labels=labels)
    if isinstance(x, pd.Series):
        assert isinstance(result, pd.Series)
        assert isinstance(result.dtype, pd.CategoricalDtype)
    elif labels is False:
        assert isinstance(result, np.ndarray)
    else:
        assert isinstance(result, pd.Categorical)

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), bins=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, unique=True).map(sorted), right=st.booleans(), include_lowest=st.booleans())
def test_pandas_cut_bins_subset(x, bins, right, include_lowest):
    result = pd.cut(x, bins, right=right, include_lowest=include_lowest)
    bin_intervals = pd.IntervalIndex.from_breaks(bins, closed='right' if right else 'left')
    if include_lowest:
        bin_intervals = bin_intervals.insert(0, pd.Interval(float('-inf'), bins[0], closed='left'))
    assert set(result.dtype.categories).issubset(set(bin_intervals))

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), bins=st.integers(2, 100), ordered=st.booleans())
def test_pandas_cut_ordered(x, bins, ordered):
    result = pd.cut(x, bins, ordered=ordered)
    assert result.dtype.ordered == ordered

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), bins=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2).map(sorted), duplicates=st.sampled_from(['raise', 'drop']))
def test_pandas_cut_duplicates(x, bins, duplicates):
    bins_with_duplicates = bins + [bins[-1]]
    if duplicates == 'raise':
        try:
            pd.cut(x, bins_with_duplicates, duplicates=duplicates)
            assert False, "ValueError was not raised with duplicate bins and duplicates='raise'"
        except ValueError:
            assert True
    else:
        result = pd.cut(x, bins_with_duplicates, duplicates=duplicates)
        assert len(result.dtype.categories) == len(set(bins))
# End program