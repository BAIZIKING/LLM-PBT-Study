from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_non_negative(x):
    assert np.linalg.norm(x) >= 0

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_vector_2_norm(x):
    if x.ndim == 1:
        assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(x**2)))

@given(st.arrays(np.float64, st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_matrix_frobenius_norm(x):
    if x.ndim == 2:
        assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(x**2)))
        assert np.isclose(np.linalg.norm(x, 'fro'), np.sqrt(np.sum(x**2)))

@given(st.arrays(np.float64, st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_vector_inf_norm(x):
    if x.ndim == 1:
        assert np.isclose(np.linalg.norm(x, ord=np.inf), np.max(np.abs(x)))

@given(st.arrays(np.float64, st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_matrix_norm_invariant_under_transposition(x):
    if x.ndim == 2:
        assert np.isclose(np.linalg.norm(x), np.linalg.norm(x.T))
# End program