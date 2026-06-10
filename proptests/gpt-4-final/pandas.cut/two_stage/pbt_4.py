from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# 1. Test output type property
@given(st.lists(st.integers(), min_size=1), st.integers(min_value=1), st.booleans())
def test_cut_output_type(input_list, bins, labels):
    result = pd.cut(input_list, bins, labels=labels)
    expected_type = np.ndarray if labels else pd.Series
    assert isinstance(result, expected_type)

# 2. Test length of output property
@given(st.lists(st.integers(), min_size=1), st.integers(min_value=1))
def test_cut_output_length(input_list, bins):
    result = pd.cut(input_list, bins)
    assert len(result) == len(input_list)

# 3. Test bins creation property
@given(st.integers(min_value=1, max_value=100))
def test_cut_bins_creation(num_bins):
    rng = np.random.default_rng()
    x = rng.uniform(low=-50, high=50, size=1000)
    result, returned_bins = pd.cut(x, num_bins, retbins=True)
    assert len(returned_bins) == num_bins + 1

# 4. Test NaN values handling property
@given(st.lists(st.floats(allow_nan=True), min_size=1), st.integers(min_value=1))
def test_cut_nan_handling(input_list, bins):
    result = pd.cut(input_list, bins)
    nan_indexes = [i for i, x in enumerate(input_list) if pd.isnull(x)]
    assert all(pd.isnull(result[i]) for i in nan_indexes)

# 5. Test handling of duplicates property
@given(st.lists(st.integers(min_value=1, max_value=10), min_size=2), st.integers(min_value=1))
def test_cut_duplicate_handling(input_list, bins):
    try:
        result, returned_bins = pd.cut(input_list, bins, retbins=True, duplicates='raise')
		# Number of unique bins should be equal to the number of returned bins
        unique_bins = np.unique(returned_bins)
        assert len(returned_bins) == len(unique_bins)
    except ValueError:
        # If ValueError is raised, then we have duplicate bins
        unique_bins = np.unique(input_list)
        assert len(unique_bins) < bins
# End program