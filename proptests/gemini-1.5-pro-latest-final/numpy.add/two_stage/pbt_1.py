from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays with reasonable size and element range
array_strategy = st.arrays(
    dtype=st.floats(allow_nan=False, allow_infinity=False),
    shape=st.tuples(st.integers(1, 5), st.integers(1, 5)),
    elements=st.floats(min_value=-1e6, max_value=1e6)
)

@given(x1=array_strategy, x2=array_strategy)
def test_output_datatype(x1, x2):
    """Output Datatype: The data type of the output array should match the data type of the input arrays."""
    result = np.add(x1, x2)
    assert result.dtype == np.result_type(x1, x2)

@given(x1=array_strategy, x2=array_strategy)
def test_output_shape(x1, x2):
    """Output Shape: The shape of the output array should be consistent with NumPy broadcasting rules."""
    result = np.add(x1, x2)
    expected_shape = np.broadcast(x1, x2).shape
    assert result.shape == expected_shape

@given(x1=array_strategy, x2=array_strategy)
def test_commutativity(x1, x2):
    """Commutativity: The order of operands should not affect the result."""
    result1 = np.add(x1, x2)
    result2 = np.add(x2, x1)
    assert np.allclose(result1, result2)

@given(x1=array_strategy, x2=array_strategy, x3=array_strategy)
def test_associativity(x1, x2, x3):
    """Associativity: Grouping of operands should not affect the result."""
    result1 = np.add(x1, np.add(x2, x3))
    result2 = np.add(np.add(x1, x2), x3)
    assert np.allclose(result1, result2)

@given(x=array_strategy)
def test_identity_element(x):
    """Identity Element: Adding zero to any array should not change the array."""
    result = np.add(x, 0)
    assert np.allclose(result, x)
# End program