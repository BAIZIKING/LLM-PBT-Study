from hypothesis import given, strategies as st
import numpy

# Property 1: Test output type is numpy ndarray
@given(st.lists(st.integers()))
def test_output_type_property(lst):
    a = numpy.array(lst)
    result = numpy.cumsum(a)
    assert isinstance(result, numpy.ndarray)

# Property 2: Test output datatype is determined by 'dtype' parameter
@given(st.lists(st.integers()), st.sampled_from([int, float]))
def test_dtype_property(lst, dtype):
    a = numpy.array(lst, dtype=dtype)
    assert numpy.cumsum(a).dtype == dtype

# Property 3: Test output size is same as input array size
@given(st.lists(st.integers()))
def test_size_property(lst):
    a = numpy.array(lst)
    size = a.size
    assert numpy.cumsum(a).size == size

# Property 4: Test output shape is determined by 'axis' parameter
@given(st.lists(st.lists(st.integers(), min_size=2, max_size=2), min_size=1, max_size=10))
def test_shape_property(lst):
    a = numpy.array(lst)
    shape = a.shape
    assert numpy.cumsum(a, axis=0).shape == shape
    assert numpy.cumsum(a, axis=None).shape == (shape[0]*shape[1],)

# Property 5: Test modular arithmetic for int dtype and floating point precision error
@given(st.lists(st.integers(min_value=1, max_value=10), min_size=5, max_size=5),
       st.lists(st.floats(min_value=0.1, max_value=0.9, width=32), min_size=5, max_size=5))
def test_arithmetic_property(int_lst, float_lst):
    a = numpy.array(int_lst, dtype=int)
    assert (numpy.cumsum(a)[-1] % max(int_lst)) == sum(int_lst) % max(int_lst)
    b = numpy.array(float_lst, dtype=float)
    assert abs(numpy.cumsum(b)[-1] - sum(float_lst)) <= 1e-5  # allow for float precision error