from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable values
array_strategy = st.arrays(np.float64, st.tuples(st.integers(min_value=-100, max_value=100), 
                                                 st.integers(min_value=1, max_value=5)),
                           fill=st.floats(min_value=-100, max_value=100))

# Define a strategy for generating valid norm orders
norm_order_strategy = st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2])

@given(array_strategy, norm_order_strategy)
def test_numpy_linalg_norm_non_negativity(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    assert norm_value >= 0

@given(st.arrays(np.float64, st.tuples(st.integers(min_value=1, max_value=5), 
                                    st.integers(min_value=1, max_value=5)),
                 fill=st.floats(min_value=0, max_value=0)),
       norm_order_strategy)
def test_numpy_linalg_norm_zero_vector(x, ord):
    norm_value = np.linalg.norm(x, ord=ord)
    assert norm_value == 0

@given(array_strategy, 
       st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
       norm_order_strategy)
def test_numpy_linalg_norm_scaling(x, factor, ord):
    scaled_norm = np.linalg.norm(factor * x, ord=ord)
    expected_norm = abs(factor) * np.linalg.norm(x, ord=ord)
    assert scaled_norm == expected_norm

@given(st.tuples(array_strategy, array_strategy), 
       st.sampled_from([1, 2, 'fro'])) # Focus on valid norm orders for triangle inequality
def test_numpy_linalg_norm_triangle_inequality(xy, ord):
    x, y = xy
    assert np.linalg.norm(x + y, ord=ord) <= np.linalg.norm(x, ord=ord) + np.linalg.norm(y, ord=ord)

@given(st.tuples(array_strategy, array_strategy), 
       st.sampled_from([1, 2, 'fro'])) # Focus on valid norm orders for monotonicity
def test_numpy_linalg_norm_monotonicity(xy, ord):
    x, y = xy
    condition = np.all(np.abs(x) <= np.abs(y))
    if condition:
        assert np.linalg.norm(x, ord=ord) <= np.linalg.norm(y, ord=ord)
# End program