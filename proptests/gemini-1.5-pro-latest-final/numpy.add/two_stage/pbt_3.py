from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays
array_strategy = st.arrays(dtype=float, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(allow_infinity=False, allow_nan=False))

@given(x1=array_strategy, x2=array_strategy)
def test_add_output_shape(x1, x2):
    """Output shape is the broadcast shape of inputs."""
    result = np.add(x1, x2)
    assert result.shape == np.broadcast(x1, x2).shape

@given(x1=array_strategy, x2=array_strategy, casting=st.sampled_from(['no', 'equiv', 'safe', 'same_kind', 'unsafe']))
def test_add_output_dtype(x1, x2, casting):
    """Output dtype is determined by input dtypes and casting rule."""
    result = np.add(x1, x2, casting=casting)
    expected_dtype = np.result_type(x1, x2) if casting == 'same_kind' else casting
    assert result.dtype == expected_dtype

@given(x1=array_strategy, x2=array_strategy)
def test_add_commutativity(x1, x2):
    """Commutativity: np.add(x1, x2) == np.add(x2, x1)."""
    assert np.array_equal(np.add(x1, x2), np.add(x2, x1))

@given(x1=array_strategy, x2=array_strategy, x3=array_strategy)
def test_add_associativity(x1, x2, x3):
    """Associativity: np.add(x1, np.add(x2, x3)) == np.add(np.add(x1, x2), x3)."""
    assert np.array_equal(np.add(x1, np.add(x2, x3)), np.add(np.add(x1, x2), x3))

@given(x=array_strategy)
def test_add_identity(x):
    """Identity element: Adding zero to an array results in the same array."""
    assert np.array_equal(np.add(x, 0), x)
# End program