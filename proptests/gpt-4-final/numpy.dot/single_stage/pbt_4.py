from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_dot(data):
    # Draw either an integer (scalar) or a numpy array of random dimensions
    a = data.draw(st.one_of(st.integers(), st.lists(st.integers()).map(np.array))) 
    b = data.draw(st.one_of(st.integers(), st.lists(st.integers()).map(np.array)))
    
    try:
        # If a and b are of incompatible dimensions (other than being 0-D) or if either a or b is a scalar.
        if (a.ndim != 1 and b.ndim != 1 and a.shape[-1] != b.shape[-2]) or np.isscalar(a) or np.isscalar(b):
            output = np.dot(a, b)
            assert isinstance(output, (np.int, np.ndarray))
        else:
            np.dot(a, b)
        assert False, "numpy.dot did not fail for incompatible dimensions"
    except ValueError:
        pass  # Expected for incompatible dimensions
# End program