from hypothesis import given, strategies as st
import pandas

SAFE_FLOAT = st.floats(
    min_value=-1_000_000,
    max_value=1_000_000,
    allow_nan=False,
    allow_infinity=False,
    width=32,
)


@given(st.data())
def test_pandas_cut_preserves_output_length_and_series_index(data):
    values = data.draw(st.lists(SAFE_FLOAT, min_size=1, max_size=50))
    number_of_bins = data.draw(st.integers(min_value=1, max_value=10))

    result = pandas.cut(values, number_of_bins)
    assert len(result) == len(values)

    index = [f"idx_{i}" for i in range(len(values))]
    series = pandas.Series(values, index=index)
    series_result = pandas.cut(series, number_of_bins)

    assert isinstance(series_result, pandas.Series)
    assert len(series_result) == len(series)
    assert list(series_result.index) == index


@given(st.data())
def test_pandas_cut_marks_na_and_out_of_bounds_values_as_missing(data):
    values = data.draw(
        st.lists(
            st.one_of(st.just(float("nan")), SAFE_FLOAT),
            min_size=1,
            max_size=50,
        )
    )

    bins = [0.0, 1.0, 2.0, 3.0]
    result = pandas.cut(values, bins)

    assert len(result) == len(values)

    for original_value, cut_value in zip(values, result):
        expected_missing = (
            pandas.isna(original_value)
            or original_value <= 0.0
            or original_value > 3.0
        )
        assert pandas.isna(cut_value) == expected_missing


@given(st.data())
def test_pandas_cut_interval_categories_match_explicit_bin_edges(data):
    edges = data.draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=2,
            max_size=8,
            unique=True,
        ).map(sorted)
    )
    right = data.draw(st.booleans())

    values = [(left + right_edge) / 2 for left, right_edge in zip(edges, edges[1:])]
    result = pandas.cut(values, edges, right=right)

    categories = list(result.categories)
    expected_closed = "right" if right else "left"

    assert len(categories) == len(edges) - 1

    for interval, expected_left, expected_right in zip(categories, edges, edges[1:]):
        assert interval.left == expected_left
        assert interval.right == expected_right
        assert interval.closed == expected_closed


@given(st.data())
def test_pandas_cut_labels_false_returns_valid_integer_bin_codes(data):
    values = data.draw(st.lists(SAFE_FLOAT, min_size=1, max_size=50))
    number_of_bins = data.draw(st.integers(min_value=1, max_value=20))

    codes = pandas.cut(values, number_of_bins, labels=False)

    assert len(codes) == len(values)

    for code in codes:
        assert not pandas.isna(code)
        assert int(code) == code
        assert 0 <= int(code) < number_of_bins


@given(st.data())
def test_pandas_cut_retbins_reports_effective_bins(data):
    unique_edges = data.draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=2,
            max_size=8,
            unique=True,
        ).map(sorted)
    )
    duplicate_position = data.draw(
        st.integers(min_value=0, max_value=len(unique_edges) - 1)
    )

    duplicated_edges = []
    for position, edge in enumerate(unique_edges):
        duplicated_edges.append(edge)
        if position == duplicate_position:
            duplicated_edges.append(edge)

    values = data.draw(st.lists(SAFE_FLOAT, min_size=1, max_size=30))

    _, bins_out = pandas.cut(
        values,
        duplicated_edges,
        labels=False,
        retbins=True,
        duplicates="drop",
    )

    assert list(bins_out) == unique_edges

    interval_bins = pandas.IntervalIndex.from_breaks(unique_edges, closed="right")
    _, interval_bins_out = pandas.cut(values, interval_bins, retbins=True)

    assert interval_bins_out.equals(interval_bins)


# End program