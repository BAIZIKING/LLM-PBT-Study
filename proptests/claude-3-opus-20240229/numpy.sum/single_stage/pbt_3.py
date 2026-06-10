from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate arrays of various shapes and data types.
# Use hypothesis' data() strategy to allow drawing values in sequential steps.
# This allows generating arrays with a random shape, and then generating
# random values to fill the array. Data types include integers, floats, and
# unsigned integers to test different accumulator types.
# Also generate None and tuples of ints for the axis parameter to test
# different axis inputs. Generate some NaN values to test the 'where' mask parameter.
# Properties to test:
# 1) If axis is None, output must be a scalar.
# 2) If axis is an int, output must have same number of dimensions as input, minus one.
# 3) If axis is tuple of ints, output must have same number of dims as input minus
#    the number of axis values.
# 4) The sum of the output array must equal the sum of the flattened input array 
#    (taking NaNs into account).
# 5) If out array is provided, it must have the same shape as the expected output.
# 6) The dtype of the output must match the provided dtype, if given. Otherwise
#    it must be the same as the input dtype unless the input is an integer type
#    with lower precision than the default int.

@given(st.data())
def test_numpy_sum(data):
    shape = data.draw(st.tuples(st.integers(0, 5), st.integers(0, 5), st.integers(0, 5)))
    dtype = data.draw(st.one_of(st.just(np.int8), st.just(np.int16), st.just(np.int32), 
                                st.just(np.uint8), st.just(np.uint16), st.just(np.uint32),
                                st.just(np.float16), st.just(np.float32), st.just(np.float64)))
    
    a = data.draw(st.arrays(shape=shape, dtype=dtype))

    axis = data.draw(st.one_of(st.none(), 
                               st.integers(-len(shape), len(shape)-1), 
                               st.tuples(st.integers(-len(shape), len(shape)-1), 
                                         st.integers(-len(shape), len(shape)-1))))
    where_mask = data.draw(st.arrays(shape=shape, dtype=bool))
    a[where_mask] = np.nan

    out_dtype = data.draw(st.one_of(st.none(), st.just(np.int8), st.just(np.int16), 
                                    st.just(np.int32), st.just(np.uint8), st.just(np.uint16), 
                                    st.just(np.uint32), st.just(np.float16), st.just(np.float32),
                                    st.just(np.float64)))
    
    result = np.sum(a, axis=axis, dtype=out_dtype, where=where_mask)
    
    if axis is None:
        assert np.isscalar(result)
    elif isinstance(axis, int):
        assert len(result.shape) == len(a.shape) - 1
    else:
        assert len(result.shape) == len(a.shape) - len(axis)
    
    nan_mask = ~np.isnan(a)
    assert np.allclose(result.sum(), np.sum(a[nan_mask & where_mask]))
    
    if out_dtype:
        assert result.dtype == out_dtype
    elif np.issubdtype(dtype, np.integer) and np.iinfo(dtype).bits < np.iinfo(np.int_).bits:
        if np.issubdtype(dtype, np.unsignedinteger):
            assert result.dtype == np.uint
        else:
            assert result.dtype == np.int_
    else:
        assert result.dtype == dtype
        
# End program