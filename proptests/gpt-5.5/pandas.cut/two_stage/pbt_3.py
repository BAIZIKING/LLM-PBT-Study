from hypothesis import given, strategies as st
import pandas

FINITE_FLOAT = st.floats(
    min_value=-1000.0,
    max_value=1000.0,
    allow_nan=False,
    allow_infinity=False,
    width=32,
)

FLOAT_OR_NAN = st.one_of(FINITE_FLOAT, st.just(float("nan")))

BIN_FOCUSED_VALUE = st.one_of(
    st.floats(
        min_value=-10.0,
        max_value=40.0,
        allow_nan=False,
        allow_infinity=False,
        width=32,
    ),
    st.sampled_from(
        [
            float("nan"),
            -1.0,
            0.0,
            1.0,
            2.0,
            3.0,
            10.0,
            20.0,
            30.0,
            40.0,
        ]
    ),
)


def is_missing(value):
    return bool(pandas.isna(value))


@given(st.data())
def test_pandas_cut_preserves_series_length_and_index(data):
    values = data.draw(st.lists(FLOAT_OR_NAN, min_size=0, max_size=50))
    index = [f"row_{i}" for i in range(len(values))]
    series = pandas.Series(values, index=index)

    result = pandas.cut(series, bins=[-1000.0, -1.0, 0.0, 1.0, 1000.0])

    assert isinstance(result, pandas.Series)
    assert len(result) == len(series)
    assert result.index.equals(series.index)


@given(st.data())
def test_pandas_cut_assigns_values_to_expected_bins_or_missing(data):
    values = data.draw(st.lists(BIN_FOCUSED_VALUE, min_size=0, max_size=50))

    result = pandas.cut(values, bins=[0.0, 1.0, 2.0, 3.0], labels=False)

    assert len(result) == len(values)

    for value, code in zip(values, result):
        if is_missing(value) or not (0.0 < value <= 3.0):
            assert is_missing(code)
        else:
            assert not is_missing(code)
            if value <= 1.0:
                expected = 0
            elif value <= 2.0:
                expected = 1
            else:
                expected = 2
            assert int(code) == expected


@given(st.data())
def test_pandas_cut_labels_false_returns_valid_integer_bin_codes(data):
    values = data.draw(st.lists(BIN_FOCUSED_VALUE, min_size=0, max_size=50))

    result = pandas.cut(
        values,
        bins=[0.0, 10.0, 20.0, 30.0],
        labels=False,
        include_lowest=True,
    )

    assert len(result) == len(values)

    for code in result:
        if not is_missing(code):
            assert float(code).is_integer()
            assert 0 <= int(code) < 3


@given(st.data())
def test_pandas_cut_with_labels_only_outputs_given_labels_or_missing(data):
    values = data.draw(st.lists(BIN_FOCUSED_VALUE, min_size=0, max_size=50))
    labels = ["low", "middle", "high"]

    result = pandas.cut(
        values,
        bins=[0.0, 1.0, 2.0, 3.0],
        labels=labels,
        ordered=True,
    )

    assert len(result) == len(values)
    assert list(result.categories) == labels
    assert result.ordered is True

    for value in result:
        if not is_missing(value):
            assert value in labels


@given(st.data())
def test_pandas_cut_retbins_with_duplicates_drop_returns_unique_used_bins(data):
    values = data.draw(st.lists(BIN_FOCUSED_VALUE, min_size=0, max_size=50))

    result, returned_bins = pandas.cut(
        values,
        bins=[0.0, 1.0, 1.0, 2.0, 3.0],
        labels=False,
        retbins=True,
        duplicates="drop",
    )

    returned_bins_list = list(returned_bins)

    assert len(result) == len(values)
    assert returned_bins_list == [0.0, 1.0, 2.0, 3.0]
    assert len(set(returned_bins_list)) == len(returned_bins_list)

    for code in result:
        if not is_missing(code):
            assert float(code).is_integer()
            assert 0 <= int(code) < len(returned_bins_list) - 1
# End program