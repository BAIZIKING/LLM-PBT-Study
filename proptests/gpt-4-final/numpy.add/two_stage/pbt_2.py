from hypothesis import given, strategies as st
import numpy as np

@given(st.lists(st.integers()), st.lists(st.integers()))
def test_shape_consistency(x, y):
    result = np.add(x, y)
    assert np.broadcast(x, y).shape == result.shape

@given(st.lists(st.integers()), st.lists(st.integers()))
def test_elementwise_addition(x, y):
    result = np.add(x, y)
    for i in range(min(len(x), len(y))):
        assert x[i] + y[i] == result[i]

@given(st.integers(), st.integers())
def test_scalar_case(x, y):
    result = np.add(x, y)
    assert isinstance(result, (int, float)) and x + y == result

@given(st.lists(st.integers()), st.lists(st.integers()))
def test_operation_equivalence(x, y):
    result = np.add(x, y)
    assert np.all(x + np.array(y) == result)

@given(st.lists(st.integers(), min_size=1), st.just(np.float64))
def test_data_type(x, dtype):
    result = np.add(x, x, dtype=dtype)
    assert result.dtype == dtype