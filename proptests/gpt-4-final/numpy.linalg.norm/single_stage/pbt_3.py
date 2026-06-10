from hypothesis import given, strategies as st
import numpy as np

# Test to check properties of numpy.linalg.norm function
@given(st.data())
def test_numpy_linalg_norm(data):
    # Randomly generate array of 1 or 2 dimensions with integer or float numbers
    x = data.draw(st.one_of(
        st.lists(st.floats(), min_size=1).map(np.array),  # 1D array
        st.lists(st.lists(st.integers())).map(np.array),  # 2D array
    ))

    # Generate valid ord values
    ord_value = data.draw(st.one_of(
        st.integers(),  # non-zero integers
        st.floats(allow_nan=False, allow_infinity=False),  # finite floating numbers
        st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf])  # specific values
    ))

    # Generate valid axis values
    axis_value = data.draw(st.one_of(
        st.integers(),  # integer
        st.tuples(st.integers(), st.integers()),  # tuple of two integers
        st.none()  # None
    ))

    # Generate boolean value for keepdims
    keepdims = data.draw(st.booleans())

    if (x.ndim == 1 and ord_value in ('fro', 'nuc')) or \
            not (isinstance(ord_value, (int, float)) or ord_value in (None, 'fro', 'nuc', np.inf, -np.inf)):
        # Frobenius and nuclear norms are only defined for matrices, and invalid ord values should raise ValueError
        with pytest.raises(ValueError):
            np.linalg.norm(x, ord=ord_value, axis=axis_value, keepdims=keepdims)
    else:
        result = np.linalg.norm(x, ord=ord_value, axis=axis_value, keepdims=keepdims)
        # Confirm result is either scalar or numpy ndarray
        assert isinstance(result, (np.ndarray, np.float64))