from hypothesis import given, strategies as st
import numpy as np

# Generate a variety of array shapes, dtypes, and broadcasting patterns
# Use edge cases like empty arrays, scalars, and arrays with different shapes
# Also generate out parameter to test in-place addition
@given(
    x1=st.one_of(st.floats(), st.integers(), st.lists(st.one_of(st.floats(), st.integers()))),  
    x2=st.one_of(st.floats(), st.integers(), st.lists(st.one_of(st.floats(), st.integers()))),
    out_shape=st.one_of(st.none(), st.lists(st.integers(min_value=0), min_size=1)),
    dtype=st.one_of(st.none(), st.sampled_from([np.int32, np.int64, np.float32, np.float64])),
    where=st.one_of(st.none(), st.booleans(), st.lists(st.booleans()))
)
def test_numpy_add(x1, x2, out_shape, dtype, where):
    x1 = np.asarray(x1, dtype=dtype) 
    x2 = np.asarray(x2, dtype=dtype)
    
    kwargs = {}
    if out_shape is not None:
        kwargs['out'] = np.empty(out_shape, dtype=dtype)
    if where is not None:  
        kwargs['where'] = np.asarray(where, dtype=bool)
    
    result = np.add(x1, x2, **kwargs)
    
    # Check the result matches x1 + x2 element-wise
    assert np.allclose(result, x1 + x2)
    
    # Check shape of result matches broadcasting rules
    assert result.shape == np.broadcast(x1, x2).shape
    
    # Check dtype of result matches the specified dtype
    if dtype is not None:
        assert result.dtype == dtype
        
    # Check values of result at masked positions are unchanged    
    if 'out' in kwargs and 'where' in kwargs:
        assert np.all(result[~kwargs['where']] == kwargs['out'][~kwargs['where']])
        
# End program