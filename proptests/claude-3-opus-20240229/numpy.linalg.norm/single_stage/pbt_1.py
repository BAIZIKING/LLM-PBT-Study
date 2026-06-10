from hypothesis import given, strategies as st
import numpy as np

# Summary:
# Generate a wide variety of array inputs, including:
# - 1D and 2D arrays 
# - Different data types (int, float, complex)
# - Arrays with inf/-inf values
# - Empty arrays
# - Arrays with nan values
# - Arrays of different sizes
# Generate different axis, keepdims, and ord parameters
# Check that:
# - Norm is non-negative 
# - Norm of empty array is 0
# - Norm is invariant to multiplying input by -1
# - Specific norm calculations match expected

@given(st.data())
def test_numpy_linalg_norm(data):
    # Generate array
    elements = st.one_of(st.integers(), st.floats(), st.complex_numbers())
    shape = data.draw(st.lists(st.integers(0, 10), min_size=1, max_size=2))
    x = data.draw(st.arrays(elements, shape, unique_by=repr))

    # Add inf/-inf/nan values in some cases
    if data.draw(st.booleans()):
        x = x.astype(float)
        mask = data.draw(st.arrays(st.sampled_from([True, False]), shape, unique_by=repr))
        updates = data.draw(st.one_of(st.just(np.inf), st.just(-np.inf), st.just(np.nan))) 
        x[mask] = updates

    # Generate other params  
    ord_options = [None, data.draw(st.integers()), np.inf, -np.inf, 'fro', 'nuc']
    ord = data.draw(st.sampled_from(ord_options))
    
    axis_options = [None]
    if len(shape) == 2:
        axis_options.extend(range(-2, 2)) 
        axis_options.append(data.draw(st.tuples(st.integers(-2, 1), st.integers(-1, 1))))
    axis = data.draw(st.sampled_from(axis_options))

    keepdims = data.draw(st.booleans())

    # Check norm is non-negative
    result = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
    assert np.all(result >= 0)

    # Check norm of empty is 0  
    if 0 in x.shape:
        assert np.all(result == 0)

    # Check norm is same if input multiplied by -1
    assert np.allclose(result, np.linalg.norm(-x, ord=ord, axis=axis, keepdims=keepdims))

    # Check specific norm calculations
    if axis is None and x.ndim == 1:
        if ord == 2:
            assert np.allclose(result, np.sqrt(np.sum(np.abs(x)**2)))
        elif ord == np.inf:
            assert np.allclose(result, np.max(np.abs(x))) 
        elif ord == 1:
            assert np.allclose(result, np.sum(np.abs(x)))
    elif len(shape) == 2 and axis == (0,1):
        if ord == 'fro':
            assert np.allclose(result, np.sqrt(np.sum(np.abs(x)**2)))
# End program        