from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates diverse arrays of various shapes, data types, and edge cases.
@given(
    data=st.data(),
    shape1=st.integers(min_value=0, max_value=5),  # Up to 5 dimensions
    shape2=st.integers(min_value=0, max_value=5),
    dtype=st.sampled_from([np.int32, np.float64, np.complex128]),
)
def test_numpy_dot(data, shape1, shape2, dtype):
    # Generate arrays with random dimensions and elements.
    arr1 = data.draw(st.arrays(dtype, shape1, elements=st.floats(allow_nan=False, allow_infinity=False)))
    arr2 = data.draw(st.arrays(dtype, shape2, elements=st.floats(allow_nan=False, allow_infinity=False)))

    # Ensure compatible shapes for dot product
    if shape1 and shape2:
        arr2 = data.draw(st.arrays(dtype, shape2[:-1] + [arr1.shape[-1]], elements=st.floats(allow_nan=False, allow_infinity=False)))

    # Calculate dot product and verify properties
    result = np.dot(arr1, arr2)

    # Check shape
    if shape1 and shape2:
        assert result.shape == arr1.shape[:-1] + arr2.shape[1:]
    elif shape1 == 0 and shape2 == 0:
        assert np.isscalar(result)
    elif shape1 == 0:
        assert result.shape == arr2.shape
    else:  # shape2 == 0
        assert result.shape == arr1.shape

    # Compare with matmul or multiply
    if arr1.ndim == 2 and arr2.ndim == 2:
        assert np.allclose(result, np.matmul(arr1, arr2))
    elif arr1.ndim == 0 and arr2.ndim == 0:
        assert result == np.multiply(arr1, arr2)

    # Verify sum-product calculation for N-D arrays
    if arr1.ndim > 2 and arr2.ndim >= 2:
        i, j, k, m = data.draw(
            st.tuples(
                st.integers(min_value=0, max_value=result.shape[0] - 1),
                st.integers(min_value=0, max_value=result.shape[1] - 1),
                st.integers(min_value=0, max_value=result.shape[2] - 1),
                st.integers(min_value=0, max_value=result.shape[3] - 1),
            )
        )
        assert np.isclose(result[i, j, k, m], np.sum(arr1[i, j, :] * arr2[k, :, m]))

    # Check ValueError for incompatible shapes
    if arr1.ndim > 0 and arr2.ndim > 1 and arr1.shape[-1] != arr2.shape[-2]:
        with pytest.raises(ValueError):
            np.dot(arr1, arr2)
# End program