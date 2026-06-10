from hypothesis import given, strategies as st
import numpy as np

# Summary: 
# Generate two input arrays a and b with varying dimensions to cover different cases:
#   - Both a and b are scalars
#   - Both a and b are 1D arrays 
#   - Both a and b are 2D arrays
#   - a is ND array, b is 1D array
#   - a is ND array, b is MD array (M>=2)
# Draw random dtypes for the arrays.
# Check the following properties:
#   - Output is a scalar if both inputs are scalars or 1D arrays
#   - Output is an array otherwise
#   - Raises ValueError if dimension mismatch between a and b
#   - Result matches explicit sum product formula 
@given(st.data())
def test_numpy_dot(data):
    shape_a = data.draw(st.sampled_from([
        (), (1,), (5,), (2,3), (2,3,4)
    ]))
    shape_b = data.draw(st.sampled_from([
         (), (1,), (5,), (3,), (3,4), (4,5), (3,4,5)  
    ]))
    dtype = data.draw(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
    
    a = data.draw(st.arrays(dtype=dtype, shape=shape_a))
    b = data.draw(st.arrays(dtype=dtype, shape=shape_b))
    
    if a.ndim == 0 or b.ndim == 0 or (a.ndim == 1 and b.ndim == 1):
        assert np.isscalar(np.dot(a,b))
    else:
        assert isinstance(np.dot(a,b), np.ndarray)
    
    if a.shape[-1] != b.shape[-2]:
        with pytest.raises(ValueError):
            np.dot(a, b)

    if a.ndim >= 2 and b.ndim >= 2:
        assert (np.dot(a,b) == np.sum(a[...,None] * b[...,None,:,:],-3)).all()
# End program