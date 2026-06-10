from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable size and element values
array_strategy = st.arrays(np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), 
                           elements=st.floats(min_value=-1e6, max_value=1e6))

@given(array_strategy, 
       st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2]))
def test_norm_non_negativity(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    assert norm_value >= 0

@given(array_strategy)
def test_zero_norm_implies_zero_array(x):
    norm_value = np.linalg.norm(x)
    if norm_value == 0:
        assert np.all(x == 0)

@given(array_strategy, st.floats(min_value=-1e2, max_value=1e2, exclude_min=True, exclude_max=True))
def test_scaling_property(x, c):
    scaled_norm = np.linalg.norm(c*x)
    original_norm = np.linalg.norm(x)
    assert scaled_norm == abs(c) * original_norm 

@given(array_strategy, array_strategy, st.sampled_from([1, 2, 'fro']))
def test_triangle_inequality(x, y, ord):
    combined_norm = np.linalg.norm(x + y, ord=ord)
    separate_norms = np.linalg.norm(x, ord=ord) + np.linalg.norm(y, ord=ord)
    assert combined_norm <= separate_norms

@given(array_strategy, array_strategy)
def test_monotonicity_with_absolute_value(x, y):
    if np.all(np.abs(x) >= np.abs(y)):
        assert np.linalg.norm(x) >= np.linalg.norm(y)
# End program 