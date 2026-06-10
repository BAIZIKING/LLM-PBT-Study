from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating different input types and shapes
scalars = st.one_of(st.integers(), st.floats(), st.complex_numbers())
arrays = st.arrays(
    dtype=st.one_of(st.integers(), st.floats(), st.complex_numbers()),
    shape=st.tuples(st.integers(min_value=0), st.integers(min_value=0)),
    elements=st.floats(allow_nan=True, allow_infinity=True),
)

# Summary: Generates diverse input pairs for numpy.add, including scalars, arrays,
#          and edge cases like empty arrays and arrays with NaN/Inf.
@given(x1=st.one_of(scalars, arrays), x2=st.one_of(scalars, arrays))
def test_numpy_add(x1, x2):
    # Test element-wise addition and broadcasting
    result = np.add(x1, x2)
    expected = x1 + x2  # Use Python's + operator for expected result
    np.testing.assert_array_equal(result, expected)

    # Test in-place operation
    out = np.empty_like(result)
    np.add(x1, x2, out=out)
    np.testing.assert_array_equal(out, expected)

    # Test where argument
    where = np.random.choice([True, False], size=result.shape)
    out = np.random.rand(*result.shape)
    np.add(x1, x2, out=out, where=where)
    np.testing.assert_array_equal(out[where], expected[where])

# End program