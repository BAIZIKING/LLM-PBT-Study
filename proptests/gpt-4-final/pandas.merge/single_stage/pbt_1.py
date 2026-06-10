from hypothesis import given, strategies as st
import pytest
import pandas as pd
import numpy as np

# Create a generator for columns, which are an array of unique string values
columns = st.lists(st.text(), unique=True).map(np.array)
# Create a generator for index
index = st.lists(st.integers(), unique=True).map(np.array)

# Independent data strategy for generating DataFrame
def data_frames(columns, index):
    return st.dictionaries(columns, st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=len(index), max_size=len(index))).map(pd.DataFrame)

@given(left=data_frames(columns, index), right=data_frames(columns, index), how=st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']), on=st.text())
def test_pandas_merge(left, right, how, on):
    # Save a copy of the original data frames for later comparison
    left_original = left.copy()
    right_original = right.copy()

    # Perform the merge
    result = pd.merge(left, right, how=how, on=on, validate="warn")

    # Test that the original data frames were not modified (immutability)
    pd.testing.assert_frame_equal(left, left_original)
    pd.testing.assert_frame_equal(right, right_original)

    # Test that the output is indeed a DataFrame (type)
    assert isinstance(result, pd.DataFrame)

    # Test that the shapes of the input and the output DataFrames have the correct relationship (shape)
    if how == 'inner':
        assert len(result) <= len(left) and len(result) <= len(right)
    elif how == 'outer':
        assert len(result) >= len(left) and len(result) >= len(right)
    elif how in ('left', 'right'):
        assert len(result) == len(left) if how == 'left' else len(result) == len(right)
    elif how == 'cross':
        assert len(result) == len(left) * len(right)