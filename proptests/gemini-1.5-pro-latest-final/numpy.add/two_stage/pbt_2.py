from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(min_value=1, max_value=5), 
                                                              st.integers(min_value=1, max_value=5)), 
                            elements=st.floats(allow_nan=False, allow_infinity=False)) 

@given(x1=array_strategy, x2=array_strategy)
def test_commutativity(x1, x2):
    """Test that np.add is commutative."""
    assert np.array_equal(np.add(x1, x2), np.add(x2, x1))

@given(x1=array_strategy, x2=array_strategy, x3=array_strategy)
def test_associativity(x1, x2, x3):
    """Test that np.add is associative."""
    assert np.array_equal(np.add(np.add(x1, x2), x3), np.add(x1, np.add(x2, x3)))

@given(x=array_strategy)
def test_identity(x):
    """Test adding zero to an array does not change the array."""
    assert np.array_equal(np.add(x, 0), x)

@given(x1=array_strategy, x2=array_strategy)
def test_shape_consistency(x1, x2):
    """Test that the output shape is consistent with broadcasting rules."""
    output_shape = np.broadcast(x1, x2).shape
    assert np.add(x1, x2).shape == output_shape

@given(x1=array_strategy, x2=array_strategy)
def test_dtype_consistency(x1, x2):
    """Test that the output dtype is consistent with the input dtypes and type promotion rules."""
    output_dtype = np.result_type(x1, x2) 
    assert np.add(x1, x2).dtype == output_dtype 
# End program 