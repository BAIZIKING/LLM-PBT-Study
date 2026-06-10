from hypothesis import given, strategies as st
import numpy

#given(st.data())
# Test 1: Check DataType of Output
@given(st.lists(st.integers()), st.lists(st.integers()))
def test_dot_datatype(a, b):
    result = numpy.dot(a, b)
    assert isinstance(result, int)

# Test 2: Check shape of Output
@given(st.lists(st.lists(st.integers(), min_size=1, max_size=3)), st.lists(st.lists(st.integers(), min_size=1, max_size=3)))
def test_dot_shape(a, b):
    try:
        result = numpy.dot(a, b)
        assert result.shape == (len(a), len(b[0]))
    except ValueError:
        pass

# Test 3: Testing Exception
@given(st.lists(st.lists(st.integers(), min_size=1, max_size=3)), st.lists(st.lists(st.integers(), min_size=1, max_size=2)))
def test_dot_exception(a, b):
    try:
        numpy.dot(a, b)
    except ValueError:
        pass # If it raises a ValueError, then the test passes

# Test 4: Testing Multiply by 1
@given(st.lists(st.integers()))
def test_dot_multiply_by_1(a):
    result = numpy.dot(a, 1)
    assert numpy.array_equal(result, a)

# Test 5: Consistency
@given(st.lists(st.integers()), st.lists(st.integers()))
def test_dot_consistency(a, b):
    run_1 = numpy.dot(a, b)
    run_2 = numpy.dot(a, b)
    assert run_1 == run_2