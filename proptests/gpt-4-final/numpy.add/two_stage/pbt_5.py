from hypothesis import given, strategies as st
import numpy as np
import numpy.testing as nt

# Define a strategy to generate valid numeric numpy arrays
arrays = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=1000).map(np.array)

@given(arrays, arrays)
def test_commutativity(x1, x2):
    nt.assert_allclose(np.add(x1, x2), np.add(x2, x1))

@given(arrays, arrays)
def test_accuracy(x1, x2):
    nt.assert_allclose(np.add(x1, x2), x1 + x2)

@given(arrays, arrays)
def test_shape_consistency(x1, x2):
    try:
        result = np.add(x1, x2)
    except ValueError:
        # If x1 and x2 cannot be broadcast to a common shape, 
        # a ValueError is expected and the test should pass
        pass
    else:
        # If no exception was raised, the shapes should be broadcastable 
        # and the result should have the expected shape
        assert result.shape == np.broadcast(x1, x2).shape

# Define a strategy to generate valid scalar floats
scalars = st.floats(allow_nan=False, allow_infinity=False)

@given(scalars, scalars)
def test_scalar_and_array_handling(x1, x2):
    result = np.add(x1, x2)
    assert np.isscalar(result)

@given(arrays)
def test_identity(x):
    nt.assert_array_equal(np.add(x, 0), x)
# End program