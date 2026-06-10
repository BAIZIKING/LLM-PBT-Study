from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable size and element range
array_strategy = st.arrays(dtype=float, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), 
                           elements=st.floats(min_value=-1e5, max_value=1e5))

@given(x1=array_strategy, x2=array_strategy)
def test_commutativity(x1, x2):
    """Testing commutativity: x1 + x2 == x2 + x1"""
    assert np.array_equal(np.add(x1, x2), np.add(x2, x1))

@given(x1=array_strategy, x2=array_strategy, x3=array_strategy)
def test_associativity(x1, x2, x3):
    """Testing associativity: (x1 + x2) + x3 == x1 + (x2 + x3)"""
    assert np.array_equal(np.add(np.add(x1, x2), x3), np.add(x1, np.add(x2, x3)))

@given(x=array_strategy)
def test_identity_element(x):
    """Testing identity element: x + 0 = x"""
    zeros = np.zeros_like(x)
    assert np.array_equal(np.add(x, zeros), x)

@given(a=st.floats(min_value=-1e2, max_value=1e2), x1=array_strategy, x2=array_strategy)
def test_distributivity_over_scalar_multiplication(a, x1, x2):
    """Testing distributivity: a * (x1 + x2) == a * x1 + a * x2"""
    assert np.array_equal(np.add(a*x1, a*x2), a * np.add(x1, x2))

@given(x1=array_strategy, x2=array_strategy)
def test_shape_consistency(x1, x2):
    """Testing shape consistency: output shape follows broadcasting rules"""
    out_shape = np.broadcast(x1, x2).shape
    assert np.add(x1, x2).shape == out_shape
# End program