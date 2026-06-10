from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_non_negative(x):
    assert np.linalg.norm(x) >= 0

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_1d_vector(x):
    if x.ndim == 1:
        assert np.linalg.norm(x) == np.linalg.norm(x, ord=2)

@given(st.arrays(np.float64, (2, 2), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_2d_matrix(x):
    assert np.linalg.norm(x) == np.linalg.norm(x, ord='fro')

@given(st.arrays(np.float64, st.integers(min_value=2, max_value=5), elements=st.floats(allow_nan=False, allow_infinity=False)),
       st.integers(min_value=0, max_value=4))
def test_norm_keepdims(x, axis):
    result = np.linalg.norm(x, axis=axis, keepdims=True)
    assert result.ndim == x.ndim
    assert result.shape[axis] == 1

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_invariant_under_negation(x):
    assert np.linalg.norm(x) == np.linalg.norm(-x)
# End program