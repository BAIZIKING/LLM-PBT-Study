from hypothesis import given, strategies as st
import numpy as np

@given(st.arrays(dtype=np.int32, shape=st.integers(0, 100)))
def test_output_size(a):
    assert len(np.cumsum(a)) == len(a)
    assert len(np.cumsum(a, axis=0)) == len(a)

@given(st.arrays(dtype=np.int32, shape=st.integers(0, 100)))
def test_1d_array_axis_invariant(a):
    a = a.flatten()
    assert np.array_equal(np.cumsum(a), np.cumsum(a, axis=0))

@given(st.arrays(dtype=np.int32, shape=st.integers(0, 100)))
def test_cumsum_sum_equality(a):
    assert np.cumsum(a)[-1] == np.sum(a)

@given(st.arrays(dtype=np.int32, shape=st.integers(0, 100)), st.data())
def test_cumsum_partial_sum_equality(a, data):
    i = data.draw(st.integers(0, len(a) - 1))
    assert np.cumsum(a)[i] == np.sum(a[:i+1])

@given(st.arrays(dtype=np.int32, shape=st.integers(0, 100)))
def test_cumsum_monotonically_increasing(a):
    cumsum_a = np.cumsum(a)
    assert np.all(cumsum_a[1:] >= cumsum_a[:-1])
# End program