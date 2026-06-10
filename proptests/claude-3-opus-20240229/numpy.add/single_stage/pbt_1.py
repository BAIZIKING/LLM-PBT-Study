from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of array shapes and data types to test broadcasting
# and type promotion rules. Include scalar inputs and arrays of different 
# dimensionality. Generate some arrays that cannot be broadcast together.
# Draw boolean arrays for the where parameter.
@given(st.data())
def test_numpy_add(data):
    shape1 = data.draw(st.lists(st.integers(0, 5), min_size=0, max_size=3))
    shape2 = data.draw(st.lists(st.integers(0, 5), min_size=0, max_size=3))
    dtype1 = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64, 
                                        np.uint8, np.uint16, np.uint32, np.uint64,
                                        np.float16, np.float32, np.float64]))
    dtype2 = data.draw(st.sampled_from([np.int8, np.int16, np.int32, np.int64,
                                        np.uint8, np.uint16, np.uint32, np.uint64, 
                                        np.float16, np.float32, np.float64]))
    x1 = data.draw(st.arrays(dtype1, shape=shape1))
    x2 = data.draw(st.arrays(dtype2, shape=shape2))
    
    out_shape = data.draw(st.lists(st.integers(0, 5), min_size=0, max_size=3))
    out_dtype = data.draw(st.sampled_from([None, np.int8, np.int16, np.int32, np.int64,
                                           np.uint8, np.uint16, np.uint32, np.uint64,
                                           np.float16, np.float32, np.float64]))
    out = data.draw(st.one_of(st.none(), st.arrays(out_dtype, shape=out_shape)))
    
    where = data.draw(st.arrays(bool, shape=out_shape))
    
    try:
        result = np.add(x1, x2, out=out, where=where)
        
        # check result matches x1 + x2 for array broadcasting
        expected = x1 + x2
        assert np.all(np.isclose(result, expected, equal_nan=True))
        
        # check out parameter 
        if out is not None:
            assert result is out
            assert result.dtype == out_dtype
        else:
            assert result.dtype == np.result_type(x1, x2)
            
        # check where mask
        if where is not True:
            assert np.all(np.logical_or(result == expected, ~where))
            
    except ValueError:
        assert not np.can_cast(x1.dtype, x2.dtype) or not np.can_cast(x2.dtype, x1.dtype)
        assert not np.can_cast(np.result_type(x1, x2), out_dtype)
        assert x1.shape != x2.shape or result.shape != np.broadcast(x1, x2).shape
# End program        