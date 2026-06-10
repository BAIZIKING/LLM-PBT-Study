from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
def test_idempotence_property(lst):
    x = np.array(lst)
    assert np.isclose(np.linalg.norm(np.linalg.norm(x)), np.linalg.norm(x))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
def test_positive_definiteness_property(lst):
    x = np.array(lst)
    assert np.linalg.norm(x) >= 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
def test_consistency_property(lst):
    x = np.array(lst)
    assert np.isclose(np.linalg.norm(x), np.linalg.norm(x))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), st.floats(allow_nan=False, allow_infinity=False))
def test_scalability_property(lst, y):
    x = np.array(lst)
    assert np.isclose(np.linalg.norm(y*x), np.abs(y)*np.linalg.norm(x))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100), st.floats(allow_nan=False, allow_infinity=False, exclude=0.0))
def test_datum_dependency_property(lst, k):
    x = np.array(lst)
    y = k * x
    assert not np.isclose(np.linalg.norm(x), np.linalg.norm(y))
# End program