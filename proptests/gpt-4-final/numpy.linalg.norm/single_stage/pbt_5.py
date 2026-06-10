from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np

@given(arrays(dtype=np.float, shape=st.integers(min_value=1, max_value=10)), 
       st.one_of(st.integers(min_value=-10, max_value=10).filter(lambda x: x != 0), st.just('fro'), st.just('nuc'), st.just(np.inf), st.just(-np.inf)), 
       st.one_of(st.tuples(st.integers(min_value=0, max_value=2), st.integers(min_value=0, max_value=2)), st.none()))
def test_numpy_linalg_norm(x, ord, axis):
    result = np.linalg.norm(x, ord, axis)

    # Check whether function returns a float or ndarray
    assert isinstance(result, (float, np.ndarray))

    # Test a specific property: For ord=np.inf, result should be equal to the maximum absolute value in the array
    if ord == np.inf:
        assert result == np.max(np.abs(x))
# End program