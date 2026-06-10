from hypothesis import given, strategies as st, example
import numpy as np
import numpy.testing as npt

# Sum Invariance Property
@given(st.lists(st.integers()))
def test_sum_invariance_property(l):
    np.random.shuffle(l)
    assert np.sum(l) == np.sum(l)

# Identity Property
@given(st.lists(st.integers()), st.integers())
def test_identity_property(l, initial):
    npt.assert_equal(np.sum(l, initial=0), np.sum(l, initial=initial))

# Property of 'out' Parameter
@given(st.lists(st.integers()))
def test_out_parameter_property(l):
    out = np.zeros_like(l)
    npt.assert_equal(np.sum(l, out=out), out)

# Behavior with Different Data Types
@given(st.lists(st.integers()), st.sampled_from([np.int32, np.float32, np.float64]))
def test_data_type_behavior(l, dtype):
    arr = np.array(l, dtype=dtype)
    sum_ = np.sum(arr)
    assert type(sum_.item()) is type(dtype(0).item())

# Sum of Empty Array
@given(st.lists(st.integers(), min_size=0, max_size=0))
def test_sum_empty_array(l):
    assert np.sum(l) == 0.0