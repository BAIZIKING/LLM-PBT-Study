from hypothesis import given, strategies as st, assume
import pandas as pd
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=1))
def test_length_property(values, bins):
    result = pd.cut(values, bins)
    assert len(result) == len(values)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=1))
def test_type_property(values, bins):
    result = pd.cut(values, bins)
    assert isinstance(result, pd.Series) or isinstance(result, pd.Categorical) or isinstance(result, np.ndarray)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_binning_property(values, bins):
    assume(len(set(bins)) == len(bins))  # ensure bins are unique
    result = pd.cut(values, bins)
    for item in result:
        assert any([lower <= item.right <= upper for lower, upper in zip(bins[:-1], bins[1:])])

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=1), st.booleans())
def test_right_inclusion(values, bins, right):
    result = pd.cut(values, bins, right=right)
    for item in result:
        assert (item.left < item.right) if right else (item.left <= item.right)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=2), st.booleans())
def test_ordering_property(values, bins, ordered):
    labels = list(range(bins))
    result = pd.cut(values, bins, labels=labels, ordered=ordered)
    if ordered:
        assert all(label <= next_label for label, next_label in zip(result.categories, result.categories[1:]))
    else:
        assert all(label != next_label for label, next_label in zip(result.categories, result.categories[1:]))
# End program