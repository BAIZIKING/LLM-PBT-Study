from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates diverse arrays with varying shapes, data types, and edge cases.
@given(
    x1=st.arrays(
        dtype=st.one_of(st.integers(), st.floats(), st.complex_numbers()),
        shape=st.tuples(st.integers(0, 5), st.integers(0, 5)),
        elements=st.one_of(st.floats(allow_nan=False, allow_infinity=False), st.integers()),
    ),
    x2=st.arrays(
        dtype=st.one_of(st.integers(), st.floats(), st.complex_numbers()),
        shape=st.tuples(st.integers(0, 5), st.integers(0, 5)),
        elements=st.one_of(st.floats(allow_nan=False, allow_infinity=False), st.integers()),
    ),
)
def test_numpy_add(x1, x2):
    result_add = np.add(x1, x2)
    result_plus = x1 + x2

    # Check shape after broadcasting
    assert result_add.shape == np.broadcast(x1, x2).shape

    # Check element-wise addition
    np.testing.assert_array_equal(result_add, x1 + x2)

    # Check data type consistency
    assert result_add.dtype == np.result_type(x1, x2)

    # Check consistency with '+' operator
    np.testing.assert_array_equal(result_add, result_plus)

# End program