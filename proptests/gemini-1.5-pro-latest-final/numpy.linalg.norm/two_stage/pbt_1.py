from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays and norm orders
array_strategy = st.arrays(np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(allow_nan=False, allow_infinity=False))
ord_strategy = st.one_of(st.integers(1, 5), st.just(np.inf), st.sampled_from(["fro", "nuc"]))

@given(array_strategy)
def test_non_negativity(x):
    norm = np.linalg.norm(x)
    assert norm >= 0

@given(array_strategy)
def test_zero_norm(x):
    zero_array = np.zeros_like(x)
    assert np.linalg.norm(zero_array) == 0
    assert np.all(x == 0) if np.linalg.norm(x) == 0 else True 

@given(array_strategy, array_strategy)
def test_triangle_inequality(x, y):
    # Ensure compatible shapes for addition
    assert x.shape == y.shape
    norm_sum = np.linalg.norm(x + y)
    norm_individual = np.linalg.norm(x) + np.linalg.norm(y)
    assert norm_sum <= norm_individual

@given(array_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_homogeneity(x, a):
    norm_scaled = np.linalg.norm(a * x)
    norm_individual = abs(a) * np.linalg.norm(x)
    assert norm_scaled == norm_individual

@given(array_strategy, array_strategy, ord_strategy)
def test_monotonicity(x, y, ord):
    # Only applicable for specific norms (p-norms with p >= 1)
    if ord not in [1, 2, np.inf, "fro", "nuc"]:
        return 
    
    # Ensure compatible shapes for comparison
    assert x.shape == y.shape

    if np.all(np.abs(x) <= np.abs(y)):
        norm_x = np.linalg.norm(x, ord=ord)
        norm_y = np.linalg.norm(y, ord=ord)
        assert norm_x <= norm_y
# End program