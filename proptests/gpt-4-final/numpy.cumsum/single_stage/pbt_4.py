from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_numpy_cumsum(data):

    # Use data strategy to generate a wide variety of inputs and edge cases
    x = data.draw(st.one_of(
        st.lists(st.integers(), min_size=0, max_size=50),
        st.lists(st.floats(), min_size=0, max_size=50),
        st.lists(st.complex_numbers(), min_size=0, max_size=50),
        st.ones(dtype=np.float64, shape=1),
        st.just(np.nan),
        st.just(np.inf),
        st.lists(st.tuples(st.integers(), st.integers(), min_size=2, max_size=2)),  # for 2D array
    ))

    # Converts the list into numpy array
    a = np.array(x)

    # Generate random axis
    axis = data.draw(st.integers(min_value=0, max_value=len(a.shape) - 1))

    # Test numpy.cumsum
    result = np.cumsum(a, axis=axis)

    # check result type
    assert isinstance(result, np.ndarray)
    
    # check result length
    assert len(result) == len(a)

    # check cumsum results
    if a.size != 0:
        assert result[0] == a[0]
        if len(a.shape) > 1:
            assert np.array_equal(result.cumsum(axis=axis), a)
        else:
            assert np.sum(a) == result[-1]
    else:
        assert result.size == 0