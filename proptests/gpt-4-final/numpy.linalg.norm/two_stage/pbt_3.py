from hypothesis import given, strategies as st
import numpy as np
import numpy.linalg

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=0, max_value=10))
def test_norm_consistency(lst, ord):
    assert np.isclose(np.linalg.norm(lst, ord), np.linalg.norm(lst, ord))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=0, max_value=10))
def test_norm_output_type(lst, ord):
    assert isinstance(np.linalg.norm(lst, ord), (np.floating, np.ndarray))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=0, max_value=10))
def test_norm_non_negative(lst, ord):
    assert np.linalg.norm(lst, ord) >= 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_norm_ord_sensitivity(lst):
    assert np.linalg.norm(lst, 2) != np.linalg.norm(lst, 1)

@given(st.lists(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=2), min_size=2, max_size=2))
def test_norm_frobenius_correctness(mat):
    assert np.isclose(np.linalg.norm(mat, 'fro'), np.sqrt(np.sum(np.abs(np.array(mat))**2)))