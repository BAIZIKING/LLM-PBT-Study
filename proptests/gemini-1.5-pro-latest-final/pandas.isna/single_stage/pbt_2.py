from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generates various scalar, array, and Pandas objects with missing values.
@given(st.data())
def test_pandas_isna(data):
    # Scalars
    scalar = data.draw(st.one_of(
        st.integers(), st.floats(allow_nan=True), 
        st.text(), st.booleans(), st.none()
    ))
    result = pd.isna(scalar)
    assert isinstance(result, bool)

    # NumPy Arrays
    array = data.draw(
        st.arrays(
            dtype=st.one_of(st.integers(), st.floats(allow_nan=True)),
            shape=st.tuples(st.integers(min_value=1), st.integers(min_value=1)),
            elements=st.floats(allow_nan=True)
        )
    )
    result = pd.isna(array)
    assert isinstance(result, np.ndarray)
    assert result.shape == array.shape
    assert np.all(pd.isna(np.nan) == True)

    # Pandas Series
    series = data.draw(
        st.series(
            elements=st.one_of(
                st.integers(), st.floats(allow_nan=True),
                st.text(), st.none(), st.just(pd.NA)
            )
        )
    )
    result = pd.isna(series)
    assert isinstance(result, pd.Series)
    assert result.dtype == bool
    assert np.all(pd.isna([None, pd.NA]) == True)

    # Pandas DataFrames
    df = data.draw(
        st.data_frames(
            columns=st.column_names(),
            rows=st.lists(
                st.one_of(
                    st.integers(), st.floats(allow_nan=True),
                    st.text(), st.none(), st.just(pd.NA)
                ),
                min_size=1
            )
        )
    )
    result = pd.isna(df)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == df.shape

    # DatetimeIndex
    index = data.draw(
        st.datetimes(min_value=pd.Timestamp.min, max_value=pd.Timestamp.max) | st.just(pd.NaT)
    )
    index = pd.DatetimeIndex([index])
    result = pd.isna(index)
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert pd.isna(pd.NaT) == True
# End program