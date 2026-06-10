from hypothesis import given, strategies as st
import numpy as np
import numpy.linalg

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_numpy_linalg_norm_properties(input_list, scalar):
    x = np.array(input_list)

    # Non-Negative Output Property
    assert np.linalg.norm(x) >= 0

    # Zero Vector Norm Property
    if np.all(x == 0):
        assert np.linalg.norm(x) == 0

    # Scaling Property
    np.testing.assert_almost_equal(np.linalg.norm(scalar * x), abs(scalar) * np.linalg.norm(x))

    # As Hypothesis does not support drawing of multiple values based on previous draws,
    # Triangle Inequality will be tested in a separate function.

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_norm_triangle_inequality(x_list, y_list):
    x = np.array(x_list)
    y = np.array(y_list)

    # Triangle Inequality Property (For 2-norm)
    if len(x) == len(y): # this is required as this property only holds for vectors of equal length
        assert np.linalg.norm(x + y, ord=2) <= np.linalg.norm(x, ord=2) + np.linalg.norm(y, ord=2)
# End program