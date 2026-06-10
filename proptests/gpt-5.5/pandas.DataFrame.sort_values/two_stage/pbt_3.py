from hypothesis import given, strategies as st
import pandas


def _numeric_dataframe(draw_data, columns=("a", "b", "c"), min_rows=0, max_rows=25, allow_missing=False):
    n_rows = draw_data.draw(st.integers(min_value=min_rows, max_value=max_rows))
    if allow_missing:
        element_strategy = st.one_of(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            st.none(),
        )
    else:
        element_strategy = st.integers(min_value=-1_000_000, max_value=1_000_000)

    return pandas.DataFrame(
        {
            column: draw_data.draw(
                st.lists(element_strategy, min_size=n_rows, max_size=n_rows)
            )
            for column in columns
        }
    )


def _assert_lexicographically_ordered(frame, by, ascending):
    rows = list(frame[list(by)].itertuples(index=False, name=None))

    for left, right in zip(rows, rows[1:]):
        for index, is_ascending in enumerate(ascending):
            if left[index] == right[index]:
                continue

            if is_ascending:
                assert left[index] < right[index]
            else:
                assert left[index] > right[index]
            break


@given(st.data())
def test_pandas_DataFrame_sort_values_preserves_shape_columns_and_row_values_property(data):
    df = _numeric_dataframe(data)
    by = data.draw(st.sampled_from(["a", "b", "c"]))
    ascending = data.draw(st.booleans())

    result = df.sort_values(by=by, ascending=ascending)

    assert result.shape == df.shape
    assert list(result.columns) == list(df.columns)

    original_rows = sorted(tuple(row) for row in df.itertuples(index=False, name=None))
    result_rows = sorted(tuple(row) for row in result.itertuples(index=False, name=None))
    assert result_rows == original_rows


@given(st.data())
def test_pandas_DataFrame_sort_values_orders_by_keys_and_applies_key_property(data):
    df = _numeric_dataframe(data)

    by = data.draw(
        st.lists(
            st.sampled_from(["a", "b", "c"]),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )
    ascending = data.draw(st.lists(st.booleans(), min_size=len(by), max_size=len(by)))

    result = df.sort_values(by=by, ascending=ascending)
    _assert_lexicographically_ordered(result, by, ascending)

    key_result = df.sort_values(by="a", ascending=True, key=lambda column: -column)
    assert key_result["a"].tolist() == sorted(df["a"].tolist(), reverse=True)


@given(st.data())
def test_pandas_DataFrame_sort_values_places_missing_values_according_to_na_position_property(data):
    df = _numeric_dataframe(data, columns=("a", "b"), allow_missing=True)
    ascending = data.draw(st.booleans())
    na_position = data.draw(st.sampled_from(["first", "last"]))

    result = df.sort_values(by="a", ascending=ascending, na_position=na_position)
    values = result["a"].tolist()
    missing_flags = [pandas.isna(value) for value in values]

    if na_position == "first":
        seen_non_missing = False
        for is_missing in missing_flags:
            if is_missing:
                assert not seen_non_missing
            else:
                seen_non_missing = True
    else:
        seen_missing = False
        for is_missing in missing_flags:
            if is_missing:
                seen_missing = True
            else:
                assert not seen_missing

    non_missing_values = [value for value in values if not pandas.isna(value)]
    assert non_missing_values == sorted(non_missing_values, reverse=not ascending)


@given(st.data())
def test_pandas_DataFrame_sort_values_ignore_index_relabels_or_preserves_index_property(data):
    df = _numeric_dataframe(data)
    ascending = data.draw(st.booleans())

    result_with_original_index = df.sort_values(
        by="a",
        ascending=ascending,
        ignore_index=False,
    )
    result_with_ignored_index = df.sort_values(
        by="a",
        ascending=ascending,
        ignore_index=True,
    )

    assert list(result_with_ignored_index.index) == list(range(len(df)))
    assert sorted(result_with_original_index.index.tolist()) == list(range(len(df)))

    pandas.testing.assert_frame_equal(
        result_with_ignored_index,
        result_with_original_index.reset_index(drop=True),
    )


@given(st.data())
def test_pandas_DataFrame_sort_values_inplace_returns_none_and_matches_non_inplace_property(data):
    df = _numeric_dataframe(data)
    ascending = data.draw(st.booleans())

    expected = df.sort_values(by="a", ascending=ascending, inplace=False)

    actual = df.copy(deep=True)
    return_value = actual.sort_values(by="a", ascending=ascending, inplace=True)

    assert return_value is None
    pandas.testing.assert_frame_equal(actual, expected)


# End program