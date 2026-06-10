from hypothesis import given, strategies as st
import numpy as np

# Summary: The strategy aims to generate a diverse range of inputs for `np.cumsum` to thoroughly test its behavior. This includes:

# 1. Arrays:
#   - Varying shapes and sizes using `arrays` with different dimensions and element counts.
#   - Different data types like integers, floats, and booleans using `integers`, `floats`, and `booleans`.

# 2. Axis:
#   - Testing behavior along different axes (or None) using `integers` within the valid range for the generated array shapes.

# 3. dtype:
#   - Specifying output dtype using `sampled_from` to include common numeric types (int, float) and None.

# Properties to Check:

# 1. Output Shape: Verify that the shape of the result aligns with the expected shape based on the input array and axis.
# 2. Cumulative Sum: Ensure that each element in the result is indeed the cumulative sum of elements along the specified axis.
# 3. dtype: Check that the output array has the specified dtype (if provided).
# 4. Overflow Behavior: Test for modular arithmetic behavior when using integer types (no error on overflow).

@given(
    data=st.data(),
    shape=st.tuples(st.integers(min_value=1, max_value=3), st.integers(min_value=1, max_value=5)),
    dtype=st.sampled_from([np.int32, np.float64, None]),
    axis=st.integers(min_value=-1, max_value=1),  # Adjust based on generated dimensions
)
def test_numpy_cumsum(data, shape, dtype, axis):
    a = data.draw(st.arrays(dtype=data.draw(st.sampled_from([st.integers(), st.floats(), st.booleans()])), shape=shape))

    result = np.cumsum(a, axis=axis, dtype=dtype)

    # Check output shape
    expected_shape = list(a.shape)
    if axis is not None:
        expected_shape[axis] = 1  # Cumulative sum reduces the size along the specified axis
    assert result.shape == tuple(expected_shape)

    # Verify cumulative sum calculation
    if axis is None:
        expected_cumsum = np.cumsum(a.ravel())
    else:
        expected_cumsum = np.apply_along_axis(np.cumsum, axis, a)
    np.testing.assert_allclose(result, expected_cumsum)

    # Check output dtype
    if dtype is not None:
        assert result.dtype == dtype

    # Test overflow behavior (for integer dtypes)
    if np.issubdtype(a.dtype, np.integer) and np.issubdtype(result.dtype, np.integer):
        assert np.all((result % np.iinfo(result.dtype).max) == expected_cumsum % np.iinfo(result.dtype).max)

# End program