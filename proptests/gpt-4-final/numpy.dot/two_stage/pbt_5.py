from hypothesis import given, strategies as st
import numpy as np

@given(st.integers(), st.integers())
def test_scalar_multiplication(x, y):
    assert np.dot(x, y) == x * y

@given(st.lists(st.integers(), min_size=1), st.lists(st.integers(), min_size=1))
def test_1d_array_dot_product(a, b):
    if len(a) == len(b):
        assert np.dot(a, b) == sum(i * j for i, j in zip(a, b))

@given(st.lists(st.lists(st.integers(), min_size=1, max_size=3), min_size=1, max_size=3))
def test_2d_array_dot_product(a):
    assert type(np.dot(a, a)) == np.ndarray 

@given(st.integers(), st.lists(st.integers(), min_size=1))
def test_dot_with_scalar_and_1d_array(a, b):
    assert np.all(np.dot(a, b) == np.array([a * i for i in b]))

@given(st.lists(st.integers(), min_size=2), st.lists(st.integers(), min_size=2))
def test_incompatible_shapes(a, b):
    shape_a = np.array(a).shape[-1]
    shape_b = np.array(b).shape[-2]
    if shape_a != shape_b:
        try:
            np.dot(a, b)
            assert False, "Expected ValueError"
        except ValueError:
            pass

# End program