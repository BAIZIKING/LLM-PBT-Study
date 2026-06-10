from hypothesis import given, strategies as st
import numpy as np

# Summary: Check the properties of numpy.sum 
@given(st.data())
def test_numpy_sum(data):
    a = data.draw(st.lists(st.floats(allow_nan=True, allow_infinity=True), min_size=0, max_size=10))
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=-len(a), max_value=len(a)-1)))
    dtype = data.draw(st.sampled_from([int, float, np.int8, np.int32, np.float64, np.float128]))
    out = data.draw(st.sampled_from([None, np.array(a, dtype=dtype)]))
    keepdims = data.draw(st.booleans())
    initial = data.draw(st.floats(allow_nan=False, allow_infinity=True))
    where = data.draw(st.one_of(st.none(), st.lists(st.booleans(), min_size=len(a), max_size=len(a))))

    array_sum = np.sum(a, axis=axis, dtype=dtype, out=out, keepdims=keepdims, initial=initial, where=where)

    # if axis is set
    if axis is not None:
        assert len(a) == len(array_sum), "Length mismatch when 'axis' is set"

    # if array is empty
    if len(a) == 0:
        assert array_sum == 0.0, "Sum of an empty list is not 0"

    # if array is not empty
    elif where is None and not any(np.isnan(a)):
        assert sum(a) == array_sum, "Mismatch in array sum and built-in sum"
    
    # if there are NaNs in the array
    elif any(np.isnan(a)):
        assert np.nansum(a) == array_sum, "Mismatch in array sum and built-in sum when array contains NaNs"

# End program