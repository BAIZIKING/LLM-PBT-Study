from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, shapes=st.tuples(st.integers(min_value=1, max_value=100))))
def test_norm_non_negative(x):
    assert np.linalg.norm(x) >= 0

@given(st.arrays(np.float64, shapes=st.tuples(st.integers(min_value=1, max_value=100))))
def test_norm_1d_euclidean(x):
    if x.ndim == 1:
        assert np.linalg.norm(x) == np.sqrt(np.sum(x**2))

@given(st.arrays(np.float64, shapes=st.tuples(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))))
def test_norm_2d_frobenius(x):
    if x.ndim == 2:
        assert np.linalg.norm(x, ord='fro') == np.sqrt(np.sum(np.abs(x)**2))

@given(st.arrays(np.float64, shapes=st.tuples(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))))
def test_norm_2d_largest_singular_value(x):
    if x.ndim == 2:
        assert np.allclose(np.linalg.norm(x, ord=2), np.max(np.linalg.svd(x, compute_uv=False)))

@given(st.arrays(np.float64, shapes=st.tuples(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))), st.booleans())
def test_norm_keepdims(x, keepdims):
    result = np.linalg.norm(x, axis=1, keepdims=keepdims)
    if keepdims:
        assert result.ndim == x.ndim
        assert result.shape[1] == 1
    else:
        assert result.ndim == x.ndim - 1
# End program