from hypothesis import given, strategies as st
import pandas
import numpy as np

MISSING_VALUES = st.one_of(
    st.none(),
    st.just(np.nan),
    st.just(pandas.NA),
    st.just(pandas.NaT),
)

SCALAR_VALUES = st.one_of(
    MISSING_VALUES,
    st.booleans(),
    st.integers(min_value=-10**6, max_value=10**6),
    st.floats(allow_nan=True, allow_infinity=True, width=64),
    st.text(max_size=20),
)


@given(st.data())
def test_pandas_isna_scalar_returns_scalar_boolean(data):
    obj = data.draw(SCALAR_VALUES)

    result = pandas.isna(obj)

    assert isinstance(result, (bool, np.bool_))


@given(st.data())
def test_pandas_isna_array_like_returns_boolean_array_with_same_shape(data):
    values = data.draw(st.lists(SCALAR_VALUES, max_size=20))
    kind = data.draw(st.sampled_from(["list", "tuple", "ndarray", "index"]))

    if kind == "list":
        obj = values
    elif kind == "tuple":
        obj = tuple(values)
    elif kind == "ndarray":
        obj = np.array(values, dtype=object)
    else:
        obj = pandas.Index(values, dtype=object)

    result = pandas.isna(obj)

    assert isinstance(result, np.ndarray)
    assert result.shape == (len(values),)
    assert result.dtype == bool


@given(st.data())
def test_pandas_isna_series_and_dataframe_preserve_type_axes_and_shape(data):
    kind = data.draw(st.sampled_from(["series", "dataframe"]))

    if kind == "series":
        values = data.draw(st.lists(SCALAR_VALUES, max_size=20))
        obj = pandas.Series(
            values,
            index=pandas.Index([f"row_{i}" for i in range(len(values))], name="rows"),
            name="values",
        )

        result = pandas.isna(obj)

        assert isinstance(result, pandas.Series)
        assert result.index.equals(obj.index)
        assert result.shape == obj.shape
        if len(result) > 0:
            assert result.dtype == bool

    else:
        row_count = data.draw(st.integers(min_value=0, max_value=6))
        column_count = data.draw(st.integers(min_value=0, max_value=6))
        rows = data.draw(
            st.lists(
                st.lists(SCALAR_VALUES, min_size=column_count, max_size=column_count),
                min_size=row_count,
                max_size=row_count,
            )
        )

        obj = pandas.DataFrame(
            rows,
            index=pandas.Index([f"row_{i}" for i in range(row_count)], name="rows"),
            columns=pandas.Index(
                [f"col_{i}" for i in range(column_count)], name="columns"
            ),
        )

        result = pandas.isna(obj)

        assert isinstance(result, pandas.DataFrame)
        assert result.index.equals(obj.index)
        assert result.columns.equals(obj.columns)
        assert result.shape == obj.shape
        if result.size > 0:
            assert all(dtype == bool for dtype in result.dtypes)


@given(st.data())
def test_pandas_isna_marks_missing_values_true(data):
    obj = data.draw(MISSING_VALUES)

    result = pandas.isna(obj)

    assert bool(result) is True


@given(st.data())
def test_pandas_isna_is_elementwise_inverse_of_pandas_notna(data):
    kind = data.draw(
        st.sampled_from(["scalar", "list", "tuple", "ndarray", "index", "series", "dataframe"])
    )

    if kind == "scalar":
        obj = data.draw(SCALAR_VALUES)

    elif kind in {"list", "tuple", "ndarray", "index", "series"}:
        values = data.draw(st.lists(SCALAR_VALUES, max_size=20))

        if kind == "list":
            obj = values
        elif kind == "tuple":
            obj = tuple(values)
        elif kind == "ndarray":
            obj = np.array(values, dtype=object)
        elif kind == "index":
            obj = pandas.Index(values, dtype=object)
        else:
            obj = pandas.Series(values)

    else:
        row_count = data.draw(st.integers(min_value=0, max_value=6))
        column_count = data.draw(st.integers(min_value=0, max_value=6))
        rows = data.draw(
            st.lists(
                st.lists(SCALAR_VALUES, min_size=column_count, max_size=column_count),
                min_size=row_count,
                max_size=row_count,
            )
        )
        obj = pandas.DataFrame(rows)

    isna_result = pandas.isna(obj)
    notna_result = pandas.notna(obj)

    if isinstance(isna_result, pandas.DataFrame):
        assert isna_result.equals(~notna_result)
    elif isinstance(isna_result, pandas.Series):
        assert isna_result.equals(~notna_result)
    elif isinstance(isna_result, np.ndarray):
        assert np.array_equal(isna_result, np.logical_not(notna_result))
    else:
        assert bool(isna_result) == (not bool(notna_result))


# End program