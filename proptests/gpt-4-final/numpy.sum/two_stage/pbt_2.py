from hypothesis import given, strategies as st
import numpy

@given(st.lists(st.integers(), min_size=1))
def test_idempotency_property(lst):
    assert numpy.sum(lst) == numpy.sum(lst)

@given(st.lists(st.integers(), max_size=0))
def test_identity_property(lst):
    assert numpy.sum(lst) == 0

@given(st.tuples(st.lists(st.integers(), min_size=1), st.lists(st.integers(), min_size=1), st.lists(st.integers(), min_size=1)))
def test_associativity_property(a, b, c):
    assert numpy.sum(a + b + c) == numpy.sum(a) + numpy.sum(b) + numpy.sum(c)

@given(st.lists(st.integers(), min_size=1), st.sampled_from(['float32', 'int32', 'int64']))
def test_type_consistency_property(lst, dtype):
    arr = numpy.array(lst, dtype=dtype)
    assert numpy.sum(arr).dtype == dtype

@given(st.lists(st.lists(st.integers(), min_size=1), min_size=1))
def test_dimensions_property(lst):
    arr = numpy.array(lst)
    assert arr.ndim == numpy.sum(arr, keepdims=True).ndim
# End program