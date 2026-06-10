from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generates diverse scalar and array-like inputs for pandas.isna
@given(st.data())
def test_pandas_isna(data):
    # Generate scalar values
    scalar = data.draw(st.one_of(
        st.integers(),
        st.floats(allow_nan=True),
        st.booleans(),
        st.text(),
        st.none()
    ))

    # Generate array-like inputs
    array = data.draw(st.one_of(
        st.arrays(st.integers(), allow_nan=True),
        st.arrays(st.floats(allow_nan=True, allow_infinity=True)),
        st.arrays(st.one_of(st.text(), st.none())),
        st.datetimes(allow_nat=True)
    ))

    # Test scalar input
    result_scalar = pd.isna(scalar)
    assert isinstance(result_scalar, bool)

    # Test array-like input
    result_array = pd.isna(array)
    assert isinstance(result_array, np.ndarray)
    assert result_array.shape == array.shape

    # Check correctness for scalar and array-like inputs
    expected_result = np.array([pd.isna(x) for x in np.ravel(array)]).reshape(array.shape)
    np.testing.assert_array_equal(result_array, expected_result)

# End program