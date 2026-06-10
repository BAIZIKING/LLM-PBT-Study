from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a variety of input arrays for numpy.dot:
# - Generate 0-D (scalar), 1-D, 2-D, and N-D arrays 
# - Vary the sizes and shapes of the arrays
# - Use both integer and float dtypes
# - Generate some arrays with unequal dimensions to test error handling
# Properties to test:
# - Correctness: Result matches explicit sum product calculation
# - Raises ValueError if dimension mismatch between arrays
# - Output array has expected dimensions based on input arrays
@given(st.data())
def test_numpy_dot(data):
    # Generate a and b as either scalars, 1-D, 2-D or N-D arrays
    shape_type = data.draw(st.sampled_from(['scalar', '1d', '2d', 'nd']))
    if shape_type == 'scalar':
        a = data.draw(st.one_of(st.integers(), st.floats()))
        b = data.draw(st.one_of(st.integers(), st.floats()))
    elif shape_type == '1d':
        size = data.draw(st.integers(min_value=1, max_value=10))
        a = data.draw(st.arrays(np.float64, size, elements=st.floats(-100, 100)))
        b = data.draw(st.arrays(np.float64, size, elements=st.floats(-100, 100)))
    elif shape_type == '2d':
        rows = data.draw(st.integers(min_value=1, max_value=10))
        cols = data.draw(st.integers(min_value=1, max_value=10))
        a = data.draw(st.arrays(np.float64, (rows, cols), elements=st.floats(-100, 100))) 
        b = data.draw(st.arrays(np.float64, (cols, rows), elements=st.floats(-100, 100)))
    else: # N-D arrays
        size_a = data.draw(st.integers(min_value=1, max_value=5))
        size_b = data.draw(st.integers(min_value=1, max_value=5))
        shape_a = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=size_a, max_size=size_a))
        shape_b = data.draw(st.lists(st.integers(min_value=1, max_value=5), min_size=size_b, max_size=size_b))
        a = data.draw(st.arrays(np.float64, shape_a, elements=st.floats(-100, 100))) 
        b = data.draw(st.arrays(np.float64, shape_b, elements=st.floats(-100, 100)))
        
    # Compare to explicit sum product only for 1-D and 2-D case
    if shape_type in ['1d', '2d']:
        expected = sum(x*y for x,y in zip(a.ravel(), b.ravel()))
        assert np.allclose(np.dot(a, b), expected)
        
    # Test dimensions of result
    if shape_type == 'scalar':
        assert isinstance(np.dot(a, b), (int, float))
    elif shape_type == '1d':
        assert np.dot(a, b).shape == ()
    elif shape_type == '2d':
        assert np.dot(a, b).shape == (a.shape[0], b.shape[1])
    else:
        assert np.dot(a, b).shape == a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
        
    # Check dimension mismatch raises ValueError 
    if shape_type == 'nd':
        if a.shape[-1] != b.shape[-2]:
            with pytest.raises(ValueError):
                np.dot(a, b)
# End program