from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5).map(np.array),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=5).map(np.array))
def test_numpy_add(x, y):
    try:
        result = np.add(x, y)
    except ValueError:
        # This occurs if the inputs cannot be broadcasted
        assert x.shape != y.shape
    else:
        # Check properties
        assert result.shape == np.broadcast(x, y).shape   # output shape is as per broadcasting rules
        assert (result == x + y).all()   # output values are correct
        assert (x + y == y + x).all()   # addition is commutative
        assert np.allclose(result - y, x, equal_nan=True)  # checking if subtraction gives the original value
        assert np.isfinite(result).all()  # output contains no nan or infinite values