from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np

@given(arrays(dtype=float, shape=st.tuples(st.integers(1, 1000), st.integers(1, 1000), st.integers(1, 1000)), elements=st.floats(-1e10, 1e10)),
       arrays(dtype=float, shape=st.tuples(st.integers(1, 1000), st.integers(1, 1000), st.integers(1, 1000)), elements=st.floats(-1e10, 1e10)))
def test_numpy_add(x1, x2):
    result = np.add(x1, x2)
    # Check dimensions of result
    assert result.shape == np.broadcast(x1, x2).shape
    # Check if corresponding elements of input and output are equal.
    np.testing.assert_allclose(result, x1 + x2)
# End program