from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_non_negative(x):
    assert np.linalg.norm(x) >= 0

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_vector_euclidean(x):
    assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(np.square(x))))

@given(st.arrays(dtype=np.float64, shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_matrix_frobenius(x):
    assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(np.square(x))))

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_vector_l1(x):
    assert np.isclose(np.linalg.norm(x, ord=1), np.sum(np.abs(x)))

@given(st.arrays(dtype=np.float64, shape=st.integers(min_value=1, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_vector_inf(x):
    assert np.isclose(np.linalg.norm(x, ord=np.inf), np.max(np.abs(x)))
# End program