from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_output_size(a):
    assert len(np.cumsum(a)) == len(a)

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_output_shape_1d(a):
    assert np.cumsum(a).shape == a.shape

@given(st.arrays(dtype=st.integer(), shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
def test_output_shape_2d(a):
    assert np.cumsum(a, axis=0).shape == a.shape
    assert np.cumsum(a, axis=1).shape == a.shape
    assert np.cumsum(a).shape == (a.size,)

@given(st.arrays(dtype=st.integer(), shape=st.integers(min_value=1, max_value=100)))
def test_final_element_sum(a):
    np.testing.assert_allclose(np.cumsum(a)[-1], np.sum(a))

@given(st.arrays(dtype=st.floating(), shape=st.integers(min_value=1, max_value=100)))
def test_final_element_sum_float(a):
    np.testing.assert_allclose(np.cumsum(a)[-1], np.sum(a), rtol=1e-7, atol=1e-8)

@given(st.arrays(dtype=st.integer(), shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
def test_cumsum_axis_0(a):
    cumsum_result = np.cumsum(a, axis=0)
    for i in range(a.shape[0]):
        np.testing.assert_array_equal(cumsum_result[i], np.sum(a[:i+1], axis=0))

@given(st.arrays(dtype=st.integer(), shape=st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))))
def test_cumsum_axis_1(a):
    cumsum_result = np.cumsum(a, axis=1)
    for i in range(a.shape[1]):
        np.testing.assert_array_equal(cumsum_result[:, i], np.sum(a[:, :i+1], axis=1))
# End program