from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: The generation strategy aims to create a diverse range of inputs for the pandas.isna function, including:
# 1. Scalar values: Covering various data types like integers, floats, strings, booleans, and None.
# 2. Array-like objects: Generating NumPy arrays, Pandas Series, and Pandas DataFrames with different shapes and data types, including numeric, object, and datetimelike.
# 3. Missing values: Explicitly including NaN, None, and NaT values within the generated data to test their detection.

@given(st.data())
def test_pandas_isna(data):
    # Generate scalar values
    scalar = data.draw(st.one_of(
        st.integers(),
        st.floats(allow_nan=True),
        st.text(),
        st.booleans(),
        st.none()
    ))

    # Generate array-like objects
    array_like = data.draw(st.one_of(
        st.arrays(
            dtype=st.sampled_from([np.int64, np.float64, np.object_, np.datetime64]),
            shape=st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5)),
            elements=st.floats(allow_nan=True) | st.text() | st.none() | st.dates()
        ),
        st.dataframes(
            columns=st.integers(min_value=1, max_value=5),
            rows=st.integers(min_value=0, max_value=5),
            data=st.floats(allow_nan=True) | st.text() | st.none() | st.dates()
        ),
        st.series(
            elements=st.floats(allow_nan=True) | st.text() | st.none() | st.dates()
        )
    ))

    # Check properties based on the API documentation:
    # 1. Scalar input should return a scalar boolean.
    if np.isscalar(scalar):
        assert isinstance(pd.isna(scalar), bool)

    # 2. Array-like input should return an array of booleans with the same shape.
    else:
        result = pd.isna(array_like)
        assert isinstance(result, (np.ndarray, pd.Series, pd.DataFrame))
        assert result.shape == array_like.shape

        # 3. NaN, None, and NaT should be detected as missing.
        if isinstance(array_like, (pd.Series, pd.DataFrame)):
            assert result.any().any()  # Check if there are any True values in the result

# End program