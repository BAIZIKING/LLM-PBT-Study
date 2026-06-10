from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_dot_output_shape(data):
    a_shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    b_shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    a = data.draw(st.arrays(np.float64, shape=a_shape))
    b = data.draw(st.arrays(np.float64, shape=b_shape))
    out_shape = np.dot(a, b).shape
    assert out_shape == (a.shape[0], b.shape[1])

@given(st.arrays(np.float64, shape=st.tuples(st.integers(min_value=1, max_value=100))))
def test_numpy_dot_1d_inner_product(a):
    b = np.random.rand(a.shape[0])
    out = np.dot(a, b)
    assert isinstance(out, np.float64)
    assert np.isclose(out, np.sum(a * b))

@given(st.data())
def test_numpy_dot_2d_matrix_multiplication(data):
    shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    a = data.draw(st.arrays(np.float64, shape=shape))
    b = data.draw(st.arrays(np.float64, shape=(shape[1], shape[0])))
    out = np.dot(a, b)
    assert out.shape == (a.shape[0], b.shape[1])
    for i in range(a.shape[0]):
        for j in range(b.shape[1]):
            assert np.isclose(out[i, j], np.dot(a[i, :], b[:, j]))

@given(st.data())
def test_numpy_dot_output_dtype(data):
    a_dtype = data.draw(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
    b_dtype = data.draw(st.sampled_from([np.int32, np.int64, np.float32, np.float64]))
    a_shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    b_shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    a = data.draw(st.arrays(a_dtype, shape=a_shape))
    b = data.draw(st.arrays(b_dtype, shape=b_shape))
    out = np.dot(a, b)
    assert out.dtype == np.result_type(a_dtype, b_dtype)

@given(st.data())
def test_numpy_dot_sum_equivalence(data):
    shape = data.draw(st.tuples(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10)))
    a = data.draw(st.arrays(np.float64, shape=shape))
    b = data.draw(st.arrays(np.float64, shape=shape))
    out1 = np.dot(a, b)
    out2 = np.sum(a * b)
    assert np.isclose(out1, out2)
# End program