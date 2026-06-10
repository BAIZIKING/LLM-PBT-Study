from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating arrays
array_shapes = st.tuples(st.integers(0, 5), st.integers(0, 5))  # Varying shapes
data_types = st.sampled_from([np.int8, np.int16, np.int32, np.float32, np.complex64])
array_data = st.data()

# Summary: Generates diverse arrays and checks properties of np.add
@given(
    x1_shape=array_shapes,
    x2_shape=array_shapes,
    data_type=data_types,
    where=st.booleans(),  # Include where parameter testing
)
def test_numpy_add(x1_shape, x2_shape, data_type, where):
    # Generate input arrays with specified shapes and data type
    x1 = array_data.draw(st.arrays(data_type, shape=x1_shape))
    x2 = array_data.draw(st.arrays(data_type, shape=x2_shape))

    # Generate where mask if needed
    where_mask = np.random.randn(*x1.shape) > 0 if where else None

    # Compute result using np.add
    result = np.add(x1, x2, where=where_mask)

    # Check output shape based on broadcasting rules
    expected_shape = np.broadcast(x1, x2).shape
    assert result.shape == expected_shape

    # Check element-wise addition where where condition is True
    if where_mask is not None:
        assert np.allclose(result[where_mask], x1[where_mask] + x2[where_mask])

    # Check that unmodified elements remain unchanged
    if where_mask is not None:
        assert np.allclose(result[~where_mask], x1[~where_mask])

    # Check output data type matches input type
    assert result.dtype == data_type
# End program