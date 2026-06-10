from hypothesis import given, strategies as st
import numpy as np

def arrays(shape):
    return st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=np.prod(shape), max_size=np.prod(shape)).map(lambda x: np.array(x).reshape(shape))

shapes = st.tuples(st.integers(1, 5), st.integers(1, 5))

@given(st.tuples(arrays(shapes), arrays(shapes)))
def test_numpy_add(arrays):
    x, y = arrays
    try:
        result = np.add(x, y)
    except ValueError:
        # If the shapes of x and y aren't compatible for broadcasting,
        # numpy will raise a ValueError. In this case our test passes, since our function
        # correctly recognises that these are invalid inputs.
        pass
    else:
        # If no exception was raised, we now check that our function has the
        # properties it's supposed to.
        assert result.shape == np.broadcast(x, y).shape
        assert np.all(result == x + y)
# End program