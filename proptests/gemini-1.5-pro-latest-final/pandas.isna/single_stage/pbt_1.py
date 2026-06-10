from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: The generation strategy aims to create a diverse set of inputs for the pandas.isna function, covering various data types and edge cases.
# 1. Scalars: We generate various scalar values including integers, floats, strings, booleans, None, and NaN (using both np.nan and pd.NA).
# 2. Arrays: We create arrays of different data types (integers, floats, strings) with varying shapes and sizes. Some arrays will include missing values (NaN or None).
# 3. Datetime-like: We generate datetime-like data using pd.Timestamp and pd.DatetimeIndex, including NaT values.
@given(st.data())
def test_pandas_isna(data):
    # Generate scalar inputs
    scalar = data.draw(
        st.one_of(
            st.integers(),
            st.floats(allow_nan=True),
            st.text(),
            st.booleans(),
            st.none(),
            st.just(np.nan),
            st.just(pd.NA),
        )
    )

    # Generate array inputs
    array = data.draw(
        st.one_of(
            st.arrays(st.integers(), shape=st.tuples(st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=3))),
            st.arrays(st.floats(allow_nan=True), shape=st.tuples(st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=3))),
            st.arrays(st.text(), shape=st.tuples(st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=3))),
        )
    )

    # Generate datetime-like inputs
    datetime_like = data.draw(
        st.one_of(
            st.datetimes(),
            st.timedeltas(),
            st.just(pd.NaT),
            st.lists(st.one_of(st.datetimes(), st.timedeltas(), st.just(pd.NaT)), min_size=1),
        )
    )

    # Check properties based on documentation
    # 1. Scalar Input: Ensure pd.isna returns a scalar boolean.
    result_scalar = pd.isna(scalar)
    assert isinstance(result_scalar, bool)

    # 2. Array Input: Check if the returned array has the same shape as the input and dtype=bool.
    result_array = pd.isna(array)
    assert result_array.shape == array.shape
    assert result_array.dtype == bool

    # 3. Datetime-like Input: Verify the returned result is of the same type as the input and contains boolean values.
    result_datetime_like = pd.isna(datetime_like)
    assert isinstance(result_datetime_like, type(datetime_like))
    if isinstance(result_datetime_like, pd.DatetimeIndex):
        assert all(isinstance(x, bool) for x in result_datetime_like.values)
    else:
        assert isinstance(result_datetime_like, bool)

# End program