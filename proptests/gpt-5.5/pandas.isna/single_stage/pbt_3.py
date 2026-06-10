from hypothesis import given, strategies as st
import datetime as dt
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

# Summary: Generate scalars, Python lists, NumPy arrays, pandas Indexes, Series, and DataFrames.
# Include ordinary values plus missing sentinels: None, NaN, pd.NA, pd.NaT, datetime64 NaT, timedelta64 NaT.
# Properties: Scalars return a boolean missingness result; ndarray/list/Index inputs return boolean ndarrays
# with matching shape/length; Series/DataFrame inputs return the same pandas type with matching labels and
# elementwise missingness according to the documented missing-value rules.
@given(st.data())
def test_pandas_isna(data):
    def expected_missing_scalar(x):
        if x is None or x is pd.NA or x is pd.NaT:
            return True
        if isinstance(x, (float, np.floating)):
            return bool(np.isnan(x))
        if isinstance(x, np.datetime64):
            return bool(np.isnat(x))
        if isinstance(x, np.timedelta64):
            return bool(np.isnat(x))
        return False

    missing_scalars = st.one_of(
        st.none(),
        st.just(float("nan")),
        st.just(np.nan),
        st.just(pd.NA),
        st.just(pd.NaT),
        st.just(np.datetime64("NaT")),
        st.just(np.timedelta64("NaT")),
    )

    non_missing_scalars = st.one_of(
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=True),
        st.text(),
        st.binary(),
        st.dates(),
        st.times(),
    )

    scalar_values = st.one_of(missing_scalars, non_missing_scalars)

    def draw_values_1d(max_size=8):
        return data.draw(st.lists(scalar_values, min_size=0, max_size=max_size))

    def draw_rectangular_values(max_rows=5, max_cols=5):
        nrows = data.draw(st.integers(min_value=0, max_value=max_rows))
        ncols = data.draw(st.integers(min_value=0, max_value=max_cols))
        rows = [
            [data.draw(scalar_values) for _ in range(ncols)]
            for _ in range(nrows)
        ]
        return rows, nrows, ncols

    kind = data.draw(
        st.sampled_from(
            [
                "scalar",
                "list_1d",
                "list_2d",
                "ndarray_object_1d",
                "ndarray_object_2d",
                "ndarray_float_2d",
                "index",
                "datetime_index",
                "series",
                "dataframe",
            ]
        )
    )

    if kind == "scalar":
        obj = data.draw(scalar_values)
        result = pd.isna(obj)

        assert isinstance(result, (bool, np.bool_))
        assert bool(result) == expected_missing_scalar(obj)

    elif kind == "list_1d":
        obj = draw_values_1d()
        expected = np.array([expected_missing_scalar(x) for x in obj], dtype=bool)

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == expected.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "list_2d":
        rows, nrows, ncols = draw_rectangular_values(max_rows=5, max_cols=5)

        if nrows == 0:
            rows = [[]]
            nrows = 1
            ncols = 0

        expected = np.array(
            [[expected_missing_scalar(x) for x in row] for row in rows],
            dtype=bool,
        )

        result = pd.isna(rows)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == expected.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "ndarray_object_1d":
        values = draw_values_1d()
        obj = np.array(values, dtype=object)
        expected = np.array([expected_missing_scalar(x) for x in values], dtype=bool)

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == obj.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "ndarray_object_2d":
        rows, nrows, ncols = draw_rectangular_values(max_rows=5, max_cols=5)
        obj = np.empty((nrows, ncols), dtype=object)

        for i in range(nrows):
            for j in range(ncols):
                obj[i, j] = rows[i][j]

        expected = np.array(
            [[expected_missing_scalar(obj[i, j]) for j in range(ncols)] for i in range(nrows)],
            dtype=bool,
        ).reshape((nrows, ncols))

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == obj.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "ndarray_float_2d":
        nrows = data.draw(st.integers(min_value=0, max_value=5))
        ncols = data.draw(st.integers(min_value=0, max_value=5))
        values = data.draw(
            st.lists(
                st.floats(allow_nan=True, allow_infinity=True),
                min_size=nrows * ncols,
                max_size=nrows * ncols,
            )
        )
        obj = np.array(values, dtype=float).reshape((nrows, ncols))
        expected = np.isnan(obj)

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == obj.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "index":
        values = draw_values_1d()
        obj = pd.Index(values, dtype=object)
        expected = np.array([expected_missing_scalar(x) for x in values], dtype=bool)

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == expected.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "datetime_index":
        datetime_values = st.one_of(
            st.datetimes(
                min_value=dt.datetime(1900, 1, 1),
                max_value=dt.datetime(2200, 1, 1),
                timezones=st.none(),
            ),
            st.none(),
            st.just(pd.NaT),
            st.just(np.datetime64("NaT")),
        )
        values = data.draw(st.lists(datetime_values, min_size=0, max_size=8))
        obj = pd.DatetimeIndex(values)
        expected = np.array([expected_missing_scalar(x) for x in values], dtype=bool)

        result = pd.isna(obj)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == expected.shape
        np.testing.assert_array_equal(result, expected)

    elif kind == "series":
        values = draw_values_1d()
        name = data.draw(st.one_of(st.none(), st.text()))
        obj = pd.Series(values, index=pd.RangeIndex(len(values)), name=name, dtype=object)
        expected = pd.Series(
            [expected_missing_scalar(x) for x in values],
            index=obj.index,
            name=obj.name,
            dtype=bool,
        )

        result = pd.isna(obj)

        assert isinstance(result, pd.Series)
        assert_series_equal(result, expected)

    else:
        rows, nrows, ncols = draw_rectangular_values(max_rows=5, max_cols=5)
        obj = pd.DataFrame(rows, index=pd.RangeIndex(nrows), columns=pd.RangeIndex(ncols), dtype=object)
        expected = pd.DataFrame(
            [[expected_missing_scalar(x) for x in row] for row in rows],
            index=obj.index,
            columns=obj.columns,
            dtype=bool,
        )

        result = pd.isna(obj)

        assert isinstance(result, pd.DataFrame)
        assert_frame_equal(result, expected)
# End program