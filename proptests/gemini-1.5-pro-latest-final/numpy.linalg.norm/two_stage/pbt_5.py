from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable size and element range
reasonable_array_strategy = st.arrays(np.float64, 
                                     shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), 
                                     elements=st.floats(min_value=-1e5, max_value=1e5))

# Define a strategy for generating valid 'ord' values
ord_strategy = st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2])

@given(reasonable_array_strategy, ord_strategy)
def test_numpy_linalg_norm_non_negativity(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    assert norm_value >= 0

@given(reasonable_array_strategy, ord_strategy)
def test_numpy_linalg_norm_zero_implies_zero_vector(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    if norm_value == 0:
        assert np.all(x == 0)

@given(reasonable_array_strategy, st.floats(min_value=-1e2, max_value=1e2, exclude_zero=True), ord_strategy)
def test_numpy_linalg_norm_homogeneity(x, scale_factor, ord):
    scaled_norm = np.linalg.norm(scale_factor * x, ord=ord)
    assert scaled_norm == abs(scale_factor) * np.linalg.norm(x, ord=ord)

@given(reasonable_array_strategy, reasonable_array_strategy, st.sampled_from([1, 2, 'fro']))
def test_numpy_linalg_norm_triangle_inequality(x, y, ord):
    norm_sum = np.linalg.norm(x + y, ord=ord)
    assert norm_sum <= np.linalg.norm(x, ord=ord) + np.linalg.norm(y, ord=ord)

@given(reasonable_array_strategy, ord_strategy)
def test_numpy_linalg_norm_monotonicity_absolute_value(x, ord):
    absolute_norm = np.linalg.norm(np.abs(x), ord=ord)
    assert absolute_norm >= np.linalg.norm(x, ord=ord)
# End program