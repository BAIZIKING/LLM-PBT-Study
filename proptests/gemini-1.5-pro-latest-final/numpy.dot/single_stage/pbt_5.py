from hypothesis import given, strategies as st
import numpy as np

# Summary: The generation strategy aims to create a diverse set of inputs for `numpy.dot` to thoroughly test its behavior. 
# It considers various shapes and dtypes for the input arrays, including edge cases like scalars and 1D arrays.

@given(st.data())
def test_numpy_dot(data):
    # Generate shapes for arrays 
    shape1 = data.draw(
        st.tuples(
            st.integers(min_value=0, max_value=3),  # Up to 3 dimensions
            st.integers(min_value=1, max_value=5),  # Sizes between 1 and 5
        )
    )
    shape2 = data.draw(
        st.tuples(
            st.integers(min_value=0, max_value=3),
            st.integers(min_value=1, max_value=5),
        )
    )

    # Ensure compatible shapes for matrix multiplication
    if len(shape1) >= 2 and len(shape2) >= 2:
        shape2 = shape2[:-1] + (shape1[-1],)

    # Generate dtypes from a selection
    dtype = data.draw(st.sampled_from([np.float64, np.int32, np.complex128]))

    # Create arrays with the generated shapes and dtypes
    a = data.draw(st.arrays(dtype, shape1))
    b = data.draw(st.arrays(dtype, shape2))

    # Perform dot product
    result = np.dot(a, b)

    # Check properties based on the API documentation:

    # 1. Shape of the result:
    if len(shape1) >= 2 and len(shape2) >= 2:  # Matrix multiplication
        expected_shape = shape1[:-1] + shape2[1:]
    elif len(shape1) >= 1 and len(shape2) >= 1:  # Inner product or sum product
        expected_shape = shape1[:-1] + shape2[:-2]
    else:  # Scalar multiplication
        expected_shape = ()  # Empty tuple for scalar
    assert result.shape == expected_shape

    # 2. Dtype of the result:
    assert result.dtype == dtype

    # 3. Result with scalar inputs:
    if shape1 == () and shape2 == ():
        assert result == a * b  # Equivalent to scalar multiplication

# End program