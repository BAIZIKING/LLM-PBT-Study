from hypothesis import given, strategies as st
import numpy as np

# Define strategy for generating arrays with reasonable sizes and avoiding overflows
array_strategy = st.arrays(
    dtype=st.floats(allow_infinity=False, allow_nan=False),
    shape=st.tuples(st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5)),
    elements=st.floats(allow_infinity=False, allow_nan=False)
)

@given(x1=array_strategy, x2=array_strategy)
def test_output_shape(x1, x2):
    """Output shape matches broadcasting rules."""
    result = np.add(x1, x2)
    expected_shape = np.broadcast(x1, x2).shape
    assert result.shape == expected_shape

@given(x1=array_strategy, x2=array_strategy)
def test_data_type(x1, x2):
    """Output data type is consistent with input and casting rules."""
    result = np.add(x1, x2)
    assert result.dtype == np.result_type(x1, x2)

@given(x1=array_strategy, x2=array_strategy)
def test_commutativity(x1, x2):
    """Order of operands does not affect the result."""
    assert np.array_equal(np.add(x1, x2), np.add(x2, x1))

@given(x1=array_strategy, x2=array_strategy, x3=array_strategy)
def test_associativity(x1, x2, x3):
    """Order of operations does not affect the result."""
    assert np.array_equal(np.add(np.add(x1, x2), x3), np.add(x1, np.add(x2, x3)))

@given(x=array_strategy)
def test_identity(x):
    """Adding zero does not change the array."""
    zeros = np.zeros_like(x)
    assert np.array_equal(np.add(x, zeros), x)
# End program