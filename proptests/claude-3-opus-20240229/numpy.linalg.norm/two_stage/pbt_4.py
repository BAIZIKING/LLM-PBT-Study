from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=100)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_non_negative(x):
    assert np.linalg.norm(x) >= 0

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=100)), elements=st.just(0.0)))
def test_norm_zero_array(x):
    assert np.linalg.norm(x) == 0

@given(st.arrays(np.float64, shape=st.integers(min_value=0, max_value=100), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_1d_euclidean(x):
    assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(x**2)))

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=100), st.integers(min_value=0, max_value=100)), elements=st.floats(allow_nan=False, allow_infinity=False)))
def test_norm_2d_frobenius(x):
    assert np.isclose(np.linalg.norm(x), np.sqrt(np.sum(x**2)))

@given(st.data())
def test_norm_keepdims(data):
    x = data.draw(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)), elements=st.floats(allow_nan=False, allow_infinity=False)))
    axis = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=1), st.tuples(st.integers(min_value=0, max_value=1), st.integers(min_value=0, max_value=1))))
    keepdims = data.draw(st.booleans())
    
    result = np.linalg.norm(x, axis=axis, keepdims=keepdims)
    
    if keepdims:
        assert result.ndim == x.ndim
        assert all(dim == 1 for dim in np.array(result.shape)[np.array(axis)])
    else:
        if axis is None:
            assert result.ndim == 0
        elif isinstance(axis, int):
            assert result.ndim == x.ndim - 1
        else:
            assert result.ndim == x.ndim - len(axis)
# End program