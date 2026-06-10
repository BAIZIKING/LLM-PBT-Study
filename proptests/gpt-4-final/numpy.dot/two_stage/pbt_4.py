from hypothesis import given, strategies as st
import numpy

@given(st.lists(st.integers(), min_size=1, max_size=10), 
       st.lists(st.integers(), min_size=1, max_size=10))
def test_consistency_property(list1, list2):
    assert numpy.dot(list1, list2) == numpy.dot(list1, list2)

    
@given(st.integers(min_value=1, max_value=20), 
       st.integers(min_value=1, max_value=20),
       st.integers(min_value=1, max_value=20))
def test_shape_property(n, m, p):
    a = numpy.random.randint(10, size=(n,m))
    b = numpy.random.randint(10, size=(m,p))
    assert numpy.dot(a, b).shape == (n, p)


@given(st.integers(), st.lists(st.integers(), min_size=1, max_size=10))
def test_scalar_multiplication_property(scalar, list):
    assert numpy.dot(scalar, list) == numpy.multiply(scalar, list)


@given(st.lists(st.integers(), min_size=1, max_size=10))
def test_equality_property(list):
    assert numpy.dot(list, list) == sum([i*i for i in list])


@given(st.integers(min_value=2, max_value=4), # keeps N-D array size small to avoid slow tests
       st.integers(min_value=1, max_value=10))
def test_limit_property(n, size_of_last_dim_in_a):
    a = numpy.random.randint(10, size=([2]*n+[size_of_last_dim_in_a]))
    b = numpy.random.randint(10, size=(size_of_last_dim_in_a,))
    dot_ab = numpy.dot(a, b)
    assert dot_ab.shape == tuple([2]*n)  
    assert isinstance(dot_ab, numpy.ndarray)

# End program
