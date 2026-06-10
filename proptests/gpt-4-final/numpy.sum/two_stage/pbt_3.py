
from hypothesis import given, strategies as st
import numpy

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_commutative_property(nums):
    np.random.shuffle(nums)
    assert numpy.isclose(numpy.sum(nums), numpy.sum(nums))

@given(st.lists(st.floats()))
def test_identity_property(nums):
    nums.append(0)
    assert numpy.isclose(numpy.sum(nums), numpy.sum(nums[:-1]))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_additive_property(nums):
    mid = len(nums) // 2
    assert numpy.isclose(numpy.sum(nums), numpy.sum(nums[:mid]) + numpy.sum(nums[mid:]))

@given(st.lists(st.floats()))
def test_type_consistency(nums):
    assert isinstance(numpy.sum(nums), numpy.float64)

@given(st.lists(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), min_size=1))
def test_dimension_reduction(nums):
    assert numpy.sum(nums).ndim <= numpy.array(nums).ndim