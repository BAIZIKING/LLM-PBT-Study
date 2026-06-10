from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_output_type_1d(xs, ys):
    result = np.dot(xs, ys)
    assert isinstance(result, np.float64)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.just(1.0))
def test_output_type_scalar(xs, scalar):
    result = np.dot(xs, scalar)
    assert isinstance(result, np.ndarray)

@given(st.integers(1, 10), st.integers(1, 10))
def test_shape_conformity(m, n):
    a = np.random.rand(m, n)
    b = np.random.rand(n, m)
    result = np.dot(a, b)
    assert result.shape == (m, m)

@given(st.floats(allow_nan=False, allow_infinity=False), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_operation_check_scalar(scalar, ys):
    result = np.dot(scalar, ys)
    for y in ys:
        assert s*y in result

@given(st.floats(allow_nan=False, allow_infinity=False), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_non_commutative(scalar, ys):
    result1 = np.dot(scalar, ys)
    result2 = np.dot(ys, scalar)
    assert np.allclose(result1, result2)

#given(st.floats(allow_nan=False, allow_infinity=False), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
#def test_non_commutative_vector(a, b):
#    result1 = np.dot(a, b)
#    result2 = np.dot(b, a)
#    assert np.allclose(result1, result2)