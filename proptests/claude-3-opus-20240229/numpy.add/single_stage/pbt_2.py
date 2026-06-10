from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate a wide variety of array-like inputs x1 and x2, including
# scalars, 1D arrays, 2D arrays, and arrays with different shapes that are
# broadcastable. Test properties such as the output shape, type, and values.
@given(st.data())
def test_numpy_add(data):
    # Generate either scalars or arrays
    x1 = data.draw(st.one_of(st.floats(), st.lists(st.floats()), st.lists(st.lists(st.floats()))))
    x2 = data.draw(st.one_of(st.floats(), st.lists(st.floats()), st.lists(st.lists(st.floats()))))
    
    # If both are arrays, make sure they are broadcastable
    assume(np.array(x1).shape == np.array(x2).shape or 
           (np.array(x1).ndim == 1 and np.array(x2).ndim == 2 and len(x1) in (1, np.array(x2).shape[1])) or
           (np.array(x2).ndim == 1 and np.array(x1).ndim == 2 and len(x2) in (1, np.array(x1).shape[1])))

    out = np.add(x1, x2)
    
    # Check that the result has the expected shape
    assert out.shape == np.broadcast(np.array(x1), np.array(x2)).shape
    
    # Check that the result has the expected type
    assert out.dtype == np.result_type(np.array(x1), np.array(x2))
    
    # Check that the result has the expected values
    assert np.array_equal(out, np.array(x1) + np.array(x2))

    # Check that the out parameter works correctly
    out_array = np.zeros(out.shape)
    np.add(x1, x2, out=out_array)
    assert np.array_equal(out_array, out)

    # Check that the where parameter works correctly    
    where_array = np.array(out_array) < 1
    out_where = out_array.copy()
    np.add(x1, x2, out=out_where, where=where_array) 
    assert np.array_equal(out_where[where_array], out[where_array])
    assert np.array_equal(out_where[~where_array], out_array[~where_array])
# End program