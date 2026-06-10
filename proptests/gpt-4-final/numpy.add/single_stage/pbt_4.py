from hypothesis import given, strategies as st
import numpy as np

# The numpy.add() function has two necessary inputs (x1 and x2) which are array-like structures.
# Our strategy will be generating tuples of two elements.
# for edge cases, we use floating number which nan, inf, -inf as well as floats near 0.

@given(st.tuples(st.lists(st.floats(allow_nan=True, allow_infinity=True, min_value=-1e10, max_value=1e10), 
                            min_size=1, max_size=1e6), 
                 st.lists(st.floats(allow_nan=True, allow_infinity=True, min_value=-1e10, max_value=1e10), 
                            min_size=1, max_size=1e6)))
def test_numpy_add(arrays):
    x1, x2 = arrays

    # Numpy assertion functions are used to check common properties of NumPy arrays.
    # assert_allclose is used here to allow some tolerance on precision againt the Python built-in sum.
    # NaN, Inf and -Inf comparisons are handled effectively by this assertion function.
    np.testing.assert_allclose(np.add(x1, x2), 
                                [x + y for x, y in zip(x1, x2)], 
                                err_msg="np.add does not match with built-in Python addition")

# End program