from hypothesis import given, strategies as st
import numpy as np

# Generate a wide variety of array shapes, dimensions, and data types
# as well as scalars. Test broadcasting behavior by drawing arrays with 
# mismatched but compatible shapes. Include edge cases like empty arrays,
# arrays with zero dimensions, and floating point infinities/NaNs.
@given(
    x1=st.one_of(
        st.integers(), st.floats(allow_infinity=True, allow_nan=True),
        st.tuples(st.integers(0, 5), st.integers(0, 5)).map(lambda s: np.zeros(s)),
        st.lists(st.one_of(st.integers(), st.floats()), min_size=0, max_size=10).map(np.array)
    ),  
    x2=st.one_of(
        st.integers(), st.floats(allow_infinity=True, allow_nan=True),
        st.tuples(st.integers(0, 5), st.integers(0, 5)).map(lambda s: np.zeros(s)),
        st.lists(st.one_of(st.integers(), st.floats()), min_size=0, max_size=10).map(np.array)
    )
)
def test_numpy_add(x1, x2):
    # Check that np.add(x1, x2) matches x1 + x2 (equivalent according to docs)
    assert np.array_equal(np.add(x1, x2), x1 + x2)
    
    # Check that out parameter behaves as documented 
    out = np.zeros(np.broadcast(x1, x2).shape)
    result = np.add(x1, x2, out=out)
    assert result is out
    assert np.array_equal(result, x1 + x2)

    # Check that type promotion works as expected (e.g. int + float => float)  
    assert np.can_cast(np.add(x1, x2).dtype, np.result_type(x1, x2))
# End program