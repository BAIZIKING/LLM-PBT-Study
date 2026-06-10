from hypothesis import given, strategies as st
import numpy as np
import itertools

# Our generation strategy
def arrays(dtype, shape):
    if 'float' in dtype:
        elements = st.floats(allow_nan=False, allow_infinity=False, width=32)
    elif 'int' in dtype:
        elements = st.integers()
    else:
        elements = st.nothing()
    return st.lists(elements, min_size=np.prod(shape), max_size=np.prod(shape)).map(lambda x: np.array(x, dtype=dtype).reshape(shape))

@given(st.data())
def test_numpy_sum(data):
    # generating 1D and 2D arrays of int and float types
    dtype = data.draw(st.sampled_from(['float32', 'float64', 'int32', 'int64']))
    shape = data.draw(st.sampled_from([(10,), (10, 10)]))
    a = data.draw(arrays(dtype, shape))

    # generating axis parameter
    if len(shape) == 1:
        axis = data.draw(st.one_of(st.integers(min_value=-1, max_value=0), st.none()))
    else:
        axis = data.draw(st.one_of(st.integers(min_value=-2, max_value=1), st.none()))

    # generating out parameter
    out = np.zeros_like(a)
    
    # testing properties
    assert np.array_equal(np.sum(a, axis=axis, out=out), out)
    assert np.sum(a, axis=axis).dtype == dtype