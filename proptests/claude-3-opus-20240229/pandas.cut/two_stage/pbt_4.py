from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(data=st.data(), x=st.one_of(st.lists(st.floats(allow_nan=False, allow_infinity=False)), st.lists(st.integers())))
def test_pandas_cut_bins_match(data, x):
    bins_strategy = st.one_of(st.integers(1, 100), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    bins = data.draw(bins_strategy)
    result = pd.cut(x, bins)
    
    if isinstance(bins, int):
        assert len(result.cat.categories) == bins
    else:
        assert len(result.cat.categories) == len(bins) - 1

@given(data=st.data(), x=st.one_of(st.lists(st.floats(allow_nan=False, allow_infinity=False)), st.lists(st.integers())))
def test_pandas_cut_ordered(data, x):
    bins = data.draw(st.integers(1, 100))
    ordered = data.draw(st.booleans())
    result = pd.cut(x, bins, ordered=ordered)
    assert result.cat.ordered == ordered

@given(data=st.data(), x=st.one_of(st.lists(st.floats(allow_nan=False, allow_infinity=False)), st.lists(st.integers())))
def test_pandas_cut_labels(data, x):
    bins = data.draw(st.integers(1, 100))
    use_labels = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.lists(st.text(), min_size=bins, max_size=bins)))
    
    if use_labels and labels is not None:
        result = pd.cut(x, bins, labels=labels)
        assert isinstance(result, (pd.Series, pd.Categorical))
        assert result.dtype == object
    elif not use_labels:
        result = pd.cut(x, bins, labels=False)
        assert isinstance(result, np.ndarray)
        assert result.dtype == int
    else:
        result = pd.cut(x, bins)
        assert isinstance(result, (pd.Series, pd.Categorical))
        assert result.dtype == pd.IntervalDtype

@given(data=st.data(), x=st.one_of(st.lists(st.floats(allow_nan=True, allow_infinity=False)), st.lists(st.integers())))
def test_pandas_cut_handles_nan(data, x):
    bins = data.draw(st.integers(1, 100))
    result = pd.cut(x, bins)
    assert result[pd.isnull(x)].isnull().all()

@given(data=st.data(), x=st.one_of(st.lists(st.floats(allow_nan=False, allow_infinity=False)), st.lists(st.integers())))
def test_pandas_cut_duplicate_bins(data, x):
    bins = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100, unique=True))
    bins.append(bins[-1])  # Add a duplicate bin
    
    try:
        pd.cut(x, bins, duplicates='raise')
    except ValueError:
        pass
    else:
        result = pd.cut(x, bins, duplicates='drop')
        assert len(result.cat.categories) == len(set(bins)) - 1
# End program