from hypothesis import given, strategies as st
import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

# Summary: Generate known-missing scalars (None, NaN, pd.NA, NaT) and known-present scalars, then randomly wrap them as a scalar, ndarray, DatetimeIndex, Series, or DataFrame. Check the documented properties: scalars return a boolean, ndarrays and Indexes return boolean ndarrays with matching shape/length, and Series/DataFrame inputs return the same pandas type with preserved axes and elementwise missing-value results.
@given(st.data())
def test_pandas_isna(data):
    timestamp_strategy = st.datetimes(
        min_value=pd.Timestamp("1970-01-01").to_pydatetime(),
        max_value=pd.Timestamp("2030-12-31").to_pydatetime(),
        timezones=st.none(),
    ).map(pd.Timestamp)

    missing_element = st.sampled_from([None, np.nan, pd.NA, pd.NaT]).map(
        lambda value: (value, True)
    )
    present_element = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=True),
        st.text(),
        st.booleans(),
        timestamp_strategy,
    ).map(lambda value: (value, False))

    element = st.one_of(missing_element, present_element)

    input_kind = data.draw(
        st.sampled_from(["scalar", "ndarray", "datetime_index", "series", "dataframe"])
    )

    if input_kind == "scalar":
        value, expected = data.draw(element)

        result = pd.isna(value)

        assert isinstance(result, (bool, np.bool_))
        assert bool(result) is expected

    elif input_kind == "ndarray":
        rows = data.draw(st.integers(min_value=0, max_value=4))
        cols = data.draw(st.integers(min_value=0, max_value=4))

        values = np.empty((rows, cols), dtype=object)
        expected = np.empty((rows, cols), dtype=bool)

        for row in range(rows):
            for col in range(cols):
                value, is_missing = data.draw(element)
                values[row, col] = value
                expected[row, col] = is_missing

        result = pd.isna(values)

        assert isinstance(result, np.ndarray)
        assert result.shape == values.shape
        assert result.dtype == np.bool_
        np.testing.assert_array_equal(result, expected)

    elif input_kind == "datetime_index":
        datetime_element = st.one_of(
            st.sampled_from([None, pd.NaT]).map(lambda value: (value, True)),
            timestamp_strategy.map(lambda value: (value, False)),
        )

        size = data.draw(st.integers(min_value=0, max_value=6))
        pairs = [data.draw(datetime_element) for _ in range(size)]

        index = pd.DatetimeIndex([value for value, _ in pairs])
        expected = np.array([is_missing for _, is_missing in pairs], dtype=bool)

        result = pd.isna(index)

        assert isinstance(result, np.ndarray)
        assert result.shape == (len(index),)
        assert result.dtype == np.bool_
        np.testing.assert_array_equal(result, expected)

    elif input_kind == "series":
        size = data.draw(st.integers(min_value=0, max_value=6))
        pairs = [data.draw(element) for _ in range(size)]

        index = data.draw(
            st.lists(
                st.text(max_size=5),
                min_size=size,
                max_size=size,
                unique=True,
            )
        )
        name = data.draw(st.one_of(st.none(), st.text(max_size=5)))

        series = pd.Series([value for value, _ in pairs], index=index, name=name)
        expected = pd.Series(
            [is_missing for _, is_missing in pairs],
            index=index,
            name=name,
            dtype=bool,
        )

        result = pd.isna(series)

        assert isinstance(result, pd.Series)
        assert_series_equal(result, expected)

    else:
        rows = data.draw(st.integers(min_value=0, max_value=4))
        cols = data.draw(st.integers(min_value=0, max_value=4))

        index = data.draw(
            st.lists(
                st.text(max_size=5),
                min_size=rows,
                max_size=rows,
                unique=True,
            )
        )
        columns = data.draw(
            st.lists(
                st.text(max_size=5),
                min_size=cols,
                max_size=cols,
                unique=True,
            )
        )

        values = np.empty((rows, cols), dtype=object)
        expected_values = np.empty((rows, cols), dtype=bool)

        for row in range(rows):
            for col in range(cols):
                value, is_missing = data.draw(element)
                values[row, col] = value
                expected_values[row, col] = is_missing

        frame = pd.DataFrame(values, index=index, columns=columns)
        expected = pd.DataFrame(expected_values, index=index, columns=columns)

        result = pd.isna(frame)

        assert isinstance(result, pd.DataFrame)
        assert_frame_equal(result, expected)
# End program