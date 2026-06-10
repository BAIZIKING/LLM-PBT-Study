from hypothesis import given, strategies as st
import pandas
import numpy
import datetime

MISSING_VALUES = st.one_of(
    st.none(),
    st.just(float("nan")),
    st.just(pandas.NA),
    st.just(pandas.NaT),
)

PRESENT_VALUES = st.one_of(
    st.booleans(),
    st.integers(min_value=-10**6, max_value=10**6),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.text(max_size=20),
    st.datetimes(
        min_value=datetime.datetime(1970, 1, 1),
        max_value=datetime.datetime(2100, 12, 31),
        timezones=st.none(),
    ),
)

SCALAR_VALUES = st.one_of(MISSING_VALUES, PRESENT_VALUES)


@given(st.data())
def test_pandas_isna_scalar_returns_scalar_boolean(data):
    value = data.draw(SCALAR_VALUES)

    result = pandas.isna(value)

    assert isinstance(result, (bool, numpy.bool_))


@given(st.data())
def test_pandas_isna_ndarray_output_has_same_shape_and_boolean_dtype(data):
    rows = data.draw(st.integers(min_value=0, max_value=5))
    columns = data.draw(st.integers(min_value=0, max_value=5))
    values = data.draw(
        st.lists(SCALAR_VALUES, min_size=rows * columns, max_size=rows * columns)
    )
    array = numpy.array(values, dtype=object).reshape((rows, columns))

    result = pandas.isna(array)

    assert isinstance(result, numpy.ndarray)
    assert result.shape == array.shape
    assert result.dtype == numpy.dtype(bool)


@given(st.data())
def test_pandas_isna_preserves_series_and_dataframe_structure(data):
    series_length = data.draw(st.integers(min_value=0, max_value=10))
    series_values = data.draw(
        st.lists(SCALAR_VALUES, min_size=series_length, max_size=series_length)
    )
    series_index = pandas.Index([f"i{i}" for i in range(series_length)], name="idx")
    series = pandas.Series(series_values, index=series_index, name="values")

    series_result = pandas.isna(series)

    assert isinstance(series_result, pandas.Series)
    assert series_result.index.equals(series.index)
    assert series_result.index.name == series.index.name
    assert series_result.name == series.name
    assert series_result.shape == series.shape
    assert series_result.dtype == bool

    rows = data.draw(st.integers(min_value=0, max_value=5))
    columns = data.draw(st.integers(min_value=0, max_value=5))
    frame_values = data.draw(
        st.lists(SCALAR_VALUES, min_size=rows * columns, max_size=rows * columns)
    )
    frame_array = numpy.array(frame_values, dtype=object).reshape((rows, columns))
    frame_index = pandas.Index([f"r{i}" for i in range(rows)], name="rows")
    frame_columns = pandas.Index([f"c{i}" for i in range(columns)], name="columns")
    frame = pandas.DataFrame(frame_array, index=frame_index, columns=frame_columns)

    frame_result = pandas.isna(frame)

    assert isinstance(frame_result, pandas.DataFrame)
    assert frame_result.shape == frame.shape
    assert frame_result.index.equals(frame.index)
    assert frame_result.index.name == frame.index.name
    assert frame_result.columns.equals(frame.columns)
    assert frame_result.columns.name == frame.columns.name
    assert all(dtype == bool for dtype in frame_result.dtypes)


@given(st.data())
def test_pandas_isna_marks_missing_values_true_and_present_values_false(data):
    missing_value = data.draw(MISSING_VALUES)
    present_value = data.draw(PRESENT_VALUES)

    assert bool(pandas.isna(missing_value)) is True
    assert bool(pandas.isna(present_value)) is False


@given(st.data())
def test_pandas_isna_is_elementwise_inverse_of_pandas_notna(data):
    kind = data.draw(st.sampled_from(["scalar", "list", "array", "series", "dataframe"]))

    if kind == "scalar":
        obj = data.draw(SCALAR_VALUES)

    elif kind == "list":
        length = data.draw(st.integers(min_value=0, max_value=10))
        obj = data.draw(st.lists(SCALAR_VALUES, min_size=length, max_size=length))

    elif kind == "array":
        rows = data.draw(st.integers(min_value=0, max_value=5))
        columns = data.draw(st.integers(min_value=0, max_value=5))
        values = data.draw(
            st.lists(SCALAR_VALUES, min_size=rows * columns, max_size=rows * columns)
        )
        obj = numpy.array(values, dtype=object).reshape((rows, columns))

    elif kind == "series":
        length = data.draw(st.integers(min_value=0, max_value=10))
        values = data.draw(st.lists(SCALAR_VALUES, min_size=length, max_size=length))
        obj = pandas.Series(values)

    else:
        rows = data.draw(st.integers(min_value=0, max_value=5))
        columns = data.draw(st.integers(min_value=0, max_value=5))
        values = data.draw(
            st.lists(SCALAR_VALUES, min_size=rows * columns, max_size=rows * columns)
        )
        array = numpy.array(values, dtype=object).reshape((rows, columns))
        obj = pandas.DataFrame(array)

    isna_result = pandas.isna(obj)
    notna_result = pandas.notna(obj)

    if isinstance(isna_result, (bool, numpy.bool_)):
        assert bool(isna_result) == (not bool(notna_result))
    elif isinstance(isna_result, pandas.Series):
        assert isna_result.equals(~notna_result)
    elif isinstance(isna_result, pandas.DataFrame):
        assert isna_result.equals(~notna_result)
    else:
        assert numpy.array_equal(isna_result, numpy.logical_not(notna_result))


# End program