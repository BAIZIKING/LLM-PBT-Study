from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_add(data):
    n = data.draw(st.integers(min_value=1, max_value=10))
    m = data.draw(st.integers(min_value=1, max_value=10))

    x1 = data.draw(st.arrays(dtype=np.int32, shape=(n,)))
    x2 = data.draw(st.arrays(dtype=np.int32, shape=(n,m)), st.integers())
    
    result = np.add(x1, x2)
    
    # assert that the result is a numpy array
    assert isinstance(result, np.ndarray)
    
    # assert that the result has the same shape as the larger input
    if isinstance(x2, np.ndarray):
        assert result.shape == x2.shape
    else:
        assert result.shape == x1.shape
    
    # assert that the result equals to the sum of inputs element wise
    assert np.all(result == x1 + x2)