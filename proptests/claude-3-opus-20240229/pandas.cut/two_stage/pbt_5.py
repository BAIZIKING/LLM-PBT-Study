from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), 
       bins=st.integers(1, 100), 
       labels=st.one_of(st.none(), st.lists(st.text(), min_size=1, max_size=100)))
def test_unique_bin_count(x, bins, labels):
    if labels:
        result = pd.cut(x, bins, labels=labels)
    else:
        result = pd.cut(x, bins)
    assert len(result.cat.categories) <= (bins if not labels else min(bins, len(labels)))

@given(x=st.one_of(st.series(st.floats(allow_nan=False, allow_infinity=False)), 
                   st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)))
def test_output_shape(x):
    bins = st.integers(1, 100).example()
    result = pd.cut(x, bins)
    if isinstance(x, pd.Series):
        assert result.index.equals(x.index)
    else:
        assert len(result) == len(x)

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), 
       bins=st.integers(1, 100),
       labels=st.lists(st.text(), min_size=1, max_size=100))
def test_labels(x, bins, labels):
    result = pd.cut(x, bins, labels=labels, ordered=False)
    assert set(result.cat.categories) <= set(labels)

    result_codes = pd.cut(x, bins, labels=False)
    assert np.array_equal(result_codes, result.cat.codes)

@given(x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
       bins=st.integers(1, 100))
def test_bin_coverage(x, bins):
    result = pd.cut(x, bins)
    intervals = result.cat.categories
    assert intervals.is_non_overlapping_monotonic
    assert pd.Interval(min(x), max(x), closed='both').overlaps(intervals).all()

    oob_mask = ~pd.Series(x).apply(lambda v: intervals.contains(v).any())
    assert result[oob_mask].isna().all()

@given(data=st.data(), 
       x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),
       bins=st.integers(1, 100))
def test_returned_bins(data, x, bins):
    retbins = data.draw(st.booleans())
    result = pd.cut(x, bins, retbins=retbins)
    
    if retbins:
        assert isinstance(result, tuple) and len(result) == 2
        assert len(result[1]) == bins + 1
    else:
        assert not isinstance(result, tuple)
# End program