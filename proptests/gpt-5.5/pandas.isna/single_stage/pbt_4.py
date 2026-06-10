from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

missing_value = st.one_of(
    st.none(),
    st.just(np.nan),
    st.just(pd.NA),
    st.just(pd.NaT),
).map(lambda x: (x, True))

non_missing_value = st.one_of(
    st.booleans(),
    st.integers(min_value=-10**6, max_value=10**6),
    st.floats(allow_nan=False, allow_infinity=False, width=64),
    st.text(),
).map(lambda x: (x, False))

value_with_expected_isna = st.one_of(missing_value, non_missing_value)

float_with_expected_isna = st.one_of(
    st.floats(allow_nan=False, allow_infinity=False, width=64).map(lambda x: (x, False)),
    st.just((np.nan, True)),
)

datetime_with_expected_isna = st.one_of(
    st.datetimes(
        min_value=pd.Timestamp("1900-01-01").to_pydatetime(),
        max_value=pd.Timestamp("2100-01-01").to_pydatetime(),
    ).map(lambda x: (x, False)),
    st.none().map(lambda x: (x, True)),
    st.just((pd.NaT, True)),
)

# Summary: Generate missing and non-missing scalars, Python lists, NumPy arrays,
# pandas Index objects, Series, and DataFrames. Include documented missing-value
# edge cases: None, np.nan, pd.NA, and pd.NaT. Check that pandas.isna returns the
# documented output type, preserves shape/axes for array-like inputs, and marks
# exactly the generated missing values as True.
@given(st.data())
def test_pandas_isna(data):
    kind = data.draw(
        st.sampled_from(
            [
                "scalar",
                "list",
                "numpy_object_array",
                "numpy_float_array_2d",
                "datetime_index",
                "series",
                "dataframe",
            ]
        )
    )

    if kind == "scalar":
        value, expected = data.draw(value_with_expected_isna)
        result = pd.isna(value)

        assert isinstance(result, (bool, np.bool_))
        assert bool(result) == expected

    elif kind == "list":
        pairs = data.draw(st.lists(value_with_expected_isna, min_size=0, max_size=10))
        values = [value for value, _ in pairs]
        expected = [is_missing for _, is_missing in pairs]

        result = pd.isna(values)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == (len(values),)
        assert result.tolist() == expected

    elif kind == "numpy_object_array":
        pairs = data.draw(st.lists(value_with_expected_isna, min_size=0, max_size=10))
        values = np.array([value for value, _ in pairs], dtype=object)
        expected = [is_missing for _, is_missing in pairs]

        result = pd.isna(values)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == values.shape
        assert result.tolist() == expected

    elif kind == "numpy_float_array_2d":
        rows = data.draw(st.integers(min_value=0, max_value=5))
        cols = data.draw(st.integers(min_value=0, max_value=5))
        matrix_pairs = data.draw(
            st.lists(
                st.lists(float_with_expected_isna, min_size=cols, max_size=cols),
                min_size=rows,
                max_size=rows,
            )
        )
        values = np.array(
            [[value for value, _ in row] for row in matrix_pairs], dtype=float
        )
        expected = [[is_missing for _, is_missing in row] for row in matrix_pairs]

        result = pd.isna(values)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == values.shape
        assert result.tolist() == expected

    elif kind == "datetime_index":
        pairs = data.draw(st.lists(datetime_with_expected_isna, min_size=0, max_size=10))
        values = [value for value, _ in pairs]
        expected = [is_missing for _, is_missing in pairs]
        index = pd.DatetimeIndex(values)

        result = pd.isna(index)

        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == (len(index),)
        assert result.tolist() == expected

    elif kind == "series":
        pairs = data.draw(st.lists(value_with_expected_isna, min_size=0, max_size=10))
        values = [value for value, _ in pairs]
        expected = [is_missing for _, is_missing in pairs]
        series = pd.Series(values, name="example")

        result = pd.isna(series)

        assert isinstance(result, pd.Series)
        assert result.index.equals(series.index)
        assert result.name == series.name
        assert result.dtype == bool
        assert result.tolist() == expected

    else:
        rows = data.draw(st.integers(min_value=0, max_value=5))
        cols = data.draw(st.integers(min_value=0, max_value=5))
        matrix_pairs = data.draw(
            st.lists(
                st.lists(value_with_expected_isna, min_size=cols, max_size=cols),
                min_size=rows,
                max_size=rows,
            )
        )
        values = [[value for value, _ in row] for row in matrix_pairs]
        expected = [[is_missing for _, is_missing in row] for row in matrix_pairs]
        dataframe = pd.DataFrame(values)

        result = pd.isna(dataframe)

        assert isinstance(result, pd.DataFrame)
        assert result.index.equals(dataframe.index)
        assert result.columns.equals(dataframe.columns)
        assert result.shape == dataframe.shape
        assert result.to_numpy(dtype=bool).tolist() == expected
# End program