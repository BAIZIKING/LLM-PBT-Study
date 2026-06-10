import numpy as np
from hypothesis import given, strategies as st
import pandas as pd

# Test for output length consistency
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=1))
def test_output_length_consistency(input_array, num_bins):
    output = pd.cut(np.array(input_array), num_bins)
    assert len(output) == len(input_array)

# Test for input-output type relation
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_input_output_type_relation(input_array):
    output = pd.cut(np.array(input_array), 3)
    assert isinstance(output, pd.core.arrays.categorical.Categorical)

# Test for correct number of bins
@given(st.lists(st.integers(), min_size=1), st.integers(min_value=1))
def test_correct_number_of_bins(input_array, num_bins):
    output = pd.cut(np.array(input_array), num_bins)
    assert len(output.categories) == num_bins

# Test for handling duplicates
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_handle_duplicates(input_array):
    with pytest.raises(ValueError):
        pd.cut(np.array(input_array), [0, 1, 2, 2], duplicates='raise')
    output = pd.cut(np.array(input_array), [0, 1, 2, 2], duplicates='drop')
    assert len(output.categories) < len([0, 1, 2])

# Test for ordering of categorical output
@given(st.lists(st.floats(), st.integers(min_value=1)))
def test_ordered_categorical(input_array, num_bins):
    output = pd.cut(np.array(input_array), num_bins, ordered=True)
    assert output.ordered == True