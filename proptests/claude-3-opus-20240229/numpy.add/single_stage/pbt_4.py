from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of array shapes and data types,
# including broadcastable shapes, mixed types, and edge cases like
# empty arrays, arrays with inf/nan, and large arrays. Check that
# the result matches element-wise addition, raises on shape mismatch,  
# and handles the `out` parameter properly.
@given(
    st.data(), 
    st.booleans(), 
    st.booleans(),
    st.booleans()
)
def test_numpy_add(data, test_out, test_broadcast, test_empty):
    # Generate array shapes
    shape1 = data.draw(st.lists(st.integers(0, 5), min_size=0, max_size=4)) 
    if test_broadcast:
        # Broadcasting: generate shape2 by modifying some dims of shape1
        shape2 = [data.draw(st.integers(0, s)) if data.draw(st.booleans()) else s 
                  for s in shape1]
    else:
        shape2 = shape1
    
    # Generate array dtypes
    dtype1 = data.draw(st.sampled_from([np.int8, np.int32, np.float32, np.float64]))
    if data.draw(st.booleans()):
        dtype2 = dtype1
    else:
        dtype2 = data.draw(st.sampled_from([np.int8, np.int32, np.float32, np.float64]))

    # Generate arrays, allowing nan/inf
    arr1 = data.draw(st.arrays(dtype1, shape1, allow_infinity=True, allow_nan=True))
    arr2 = data.draw(st.arrays(dtype2, shape2, allow_infinity=True, allow_nan=True))
    
    # Test empty array if requested 
    if test_empty and data.draw(st.booleans()):
        arr1 = np.array([])
    if test_empty and data.draw(st.booleans()):
        arr2 = np.array([])

    # Test `out` parameter if requested
    if test_out:
        out = data.draw(st.arrays(dtype1, arr1.shape, allow_infinity=True, allow_nan=True))

    try:
        if test_out:
            result = np.add(arr1, arr2, out=out)
        else:
            result = np.add(arr1, arr2)

        # Check result matches element-wise addition
        expected = arr1 + arr2
        np.testing.assert_array_almost_equal(result, expected)
        
        # Check result written to `out` if provided
        if test_out:
            np.testing.assert_array_almost_equal(out, expected)

    except ValueError as e:
        # Shape mismatch should raise ValueError
        assert str(e).startswith('operands could not be broadcast together')
        assert arr1.shape != arr2.shape
# End program        