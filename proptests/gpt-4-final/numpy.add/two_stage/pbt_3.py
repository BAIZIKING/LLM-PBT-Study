from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_array_add_commutativity(x1, x2):
    np.testing.assert_array_equal(np.add(x1, x2), np.add(x2, x1))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_array_add_identity(x1):
    zeros = np.zeros_like(x1)
    np.testing.assert_array_equal(np.add(x1, zeros), x1)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_array_add_shape(x1):
    x2 = np.zeros_like(x1)
    np.testing.assert_array_equal(np.add(x1, x2).shape, x1.shape)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_array_add_elements(x1):
    x2 = np.zeros_like(x1)
    for i in range(len(x1)):
        assert np.add(x1[i], x2[i]) == x1[i]

@given(st.tuples(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.just(dtype)))
def test_array_add_type(inputs):
    x1, dtype = inputs
    x2 = np.zeros_like(x1)
    assert np.add(x1, x2, dtype=dtype).dtype == dtype
# End program