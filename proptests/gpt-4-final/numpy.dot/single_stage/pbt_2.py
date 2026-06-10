from hypothesis import given, strategies as st
import numpy as np
import numpy.testing as npt

@given(st.data())
def test_numpy_dot(data):
    # get a and b as either scalars or arrays of varying dimensions
    a = data.draw(st.one_of(st.integers(), st.floats(), st.arrays(dtype=np.float64, shape=st.tuples(st.integers(min_value=1, max_value=5)).filter(lambda x: len(x) <= 3))))
    b = data.draw(st.one_of(st.integers(), st.floats(), st.arrays(dtype=np.float64, shape=st.tuples(st.integers(min_value=1, max_value=5)).filter(lambda x: len(x) <= 3))))

    try:
        # calculate dot product
        result = np.dot(a, b)

        # verify properties based on the dimensions of a and b
        if np.ndim(a) == 0 or np.ndim(b) == 0:  # either a or b is a scalar
            npt.assert_equal(result, a * b)
        elif np.ndim(a) == 1 and np.ndim(b) == 1:  # both a and b are 1-d arrays
            npt.assert_equal(result, np.sum(a*b))
        elif np.ndim(a) == 2 and np.ndim(b) == 2:  # both a and b are 2-d arrays
            npt.assert_array_equal(result, a @ b)
        elif np.ndim(a) >= 1 and np.ndim(b) == 1:  # a is N-D array and b is a 1-D array
            npt.assert_equal(result, np.sum(a[..., :] * b))
    except ValueError:
        # check Value Error for incompatible dimensions
        assert np.ndim(a) != np.ndim(b) or (np.ndim(a) > 1 and np.ndim(b) > 1 and a.shape[-1] != b.shape[-2])