from hypothesis import given, strategies as st
import pandas
import numpy as np


_missing_scalars = st.sampled_from([None, pandas.NA, pandas.NaT, float("nan")])

_non_missing_scalars = st.one_of(
    st.booleans(),
    st.integers(min_value=-(10**9), max_value=10**9),
    st.floats(
        allow_nan=False,
        allow_infinity=False,
        width=32,
        min_value=-1e9,
        max_value=1e9,
    ),
    st.text(max_size=20),
)

_scalar_values = st.one_of(_missing_scalars, _non_missing_scalars)


def _is_known_missing(value):
    if value is None or value is pandas.NA or value is pandas.NaT:
        return True
    try:
        return bool(np.isnan(value))
    except (TypeError, ValueError):
        return False


@given(st.data())
def test_pandas_isna_scalar_output_is_boolean(data):
    value = data.draw(_scalar_values)
    result = pandas.isna(value)

    assert isinstance(result, (bool, np.bool_))


@given(st.data())
def test_pandas_isna_array_output_has_same_shape_and_positions(data):
    rows = data.draw(st.integers(min_value=0, max_value=5))
    cols = data.draw(st.integers(min_value=0, max_value=5))
    values = data.draw(
        st.lists(
            st.lists(_scalar_values, min_size=cols, max_size=cols),
            min_size=rows,
            max_size=rows,
        )
    )

    array = np.array(values, dtype=object)
    result = pandas.isna(array)

    assert isinstance(result, np.ndarray)
    assert result.shape == array.shape
    assert result.dtype == bool

    for i in range(rows):
        for j in range(cols):
            assert bool(result[i, j]) == _is_known_missing(array[i, j])


@given(st.data())
def test_pandas_isna_series_preserves_type_index_and_boolean_values(data):
    values = data.draw(st.lists(_scalar_values, min_size=0, max_size=10))
    index = pandas.Index([f"row_{i}" for i in range(len(values))])
    series = pandas.Series(values, index=index, dtype=object)

    result = pandas.isna(series)

    assert isinstance(result, pandas.Series)
    assert result.index.equals(series.index)
    assert result.dtype == bool

    for position, value in enumerate(series):
        assert bool(result.iloc[position]) == _is_known_missing(value)


@given(st.data())
def test_pandas_isna_dataframe_preserves_type_axes_shape_and_boolean_values(data):
    rows = data.draw(st.integers(min_value=0, max_value=5))
    cols = data.draw(st.integers(min_value=0, max_value=5))
    values = data.draw(
        st.lists(
            st.lists(_scalar_values, min_size=cols, max_size=cols),
            min_size=rows,
            max_size=rows,
        )
    )

    index = pandas.Index([f"row_{i}" for i in range(rows)])
    columns = pandas.Index([f"col_{j}" for j in range(cols)])
    frame = pandas.DataFrame(values, index=index, columns=columns, dtype=object)

    result = pandas.isna(frame)

    assert isinstance(result, pandas.DataFrame)
    assert result.index.equals(frame.index)
    assert result.columns.equals(frame.columns)
    assert result.shape == frame.shape
    assert all(dtype == bool for dtype in result.dtypes)

    for i in range(rows):
        for j in range(cols):
            assert bool(result.iat[i, j]) == _is_known_missing(frame.iat[i, j])


@given(st.data())
def test_pandas_isna_missing_values_are_true_and_non_missing_values_are_false(data):
    missing_value = data.draw(_missing_scalars)
    non_missing_value = data.draw(_non_missing_scalars)

    assert bool(pandas.isna(missing_value)) is True
    assert bool(pandas.isna(non_missing_value)) is False
# End program