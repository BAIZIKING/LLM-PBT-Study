from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with controlled size and element magnitude
array_strategy = st.arrays(np.float, 
                           shape=st.tuples(st.integers(1, 5), st.integers(1, 5)),
                           elements=st.floats(min_value=-1e2, max_value=1e2))

# Test for non-negativity of the norm
@given(array_strategy, st.sampled_from(np.linalg.norm_ord))
def test_norm_non_negative(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    assert norm_value >= 0

# Test if zero norm implies a zero vector/matrix
@given(array_strategy)
def test_zero_norm_implies_zero_array(x):
    norm_value = np.linalg.norm(x)
    if norm_value == 0:
        assert np.all(x == 0)

# Test the scaling property of the norm
@given(array_strategy, st.floats(min_value=-1e2, max_value=1e2))
def test_norm_scaling(x, c):
    scaled_norm = np.linalg.norm(c*x)
    expected_norm = abs(c) * np.linalg.norm(x)
    assert scaled_norm == expected_norm

# Test the triangle inequality for valid norms
@given(array_strategy, array_strategy, 
       st.sampled_from([2, np.inf, -np.inf, 1, -1]))  # Valid norms
def test_triangle_inequality(x, y, ord):
    norm_sum = np.linalg.norm(x + y, ord=ord)
    individual_norms_sum = np.linalg.norm(x, ord=ord) + np.linalg.norm(y, ord=ord)
    assert norm_sum <= individual_norms_sum

# Test monotonicity with respect to element-wise absolute values
@given(array_strategy)
def test_norm_monotonicity_absolute_value(x):
    abs_x_norm = np.linalg.norm(np.abs(x))
    original_norm = np.linalg.norm(x)
    assert abs_x_norm >= original_norm
# End program