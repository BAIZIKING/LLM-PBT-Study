from hypothesis import given, strategies as st
import pandas


_key_strategy = st.one_of(
    st.none(),
    st.integers(min_value=-3, max_value=3),
    st.text(min_size=0, max_size=3),
)


def _frame_with_key(keys, id_column):
    return pandas.DataFrame(
        {
            "k": pandas.Series(keys, dtype="object"),
            id_column: list(range(len(keys))),
        }
    )


@given(st.data())
def test_pandas_merge_key_multiplicity_property(data):
    left_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))
    right_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = _frame_with_key(left_keys, "l_id")
    right = _frame_with_key(right_keys, "r_id")

    result = pandas.merge(left, right, how=how, on="k")

    left_counts = {}
    right_counts = {}

    for key in left_keys:
        left_counts[key] = left_counts.get(key, 0) + 1

    for key in right_keys:
        right_counts[key] = right_counts.get(key, 0) + 1

    all_keys = set(left_counts) | set(right_counts)

    expected_length = 0
    for key in all_keys:
        left_count = left_counts.get(key, 0)
        right_count = right_counts.get(key, 0)

        if left_count and right_count:
            expected_length += left_count * right_count
        elif how in ("left", "outer") and left_count:
            expected_length += left_count
        elif how in ("right", "outer") and right_count:
            expected_length += right_count

    assert len(result) == expected_length


@given(st.data())
def test_pandas_merge_inner_rows_are_exact_matching_pairs_property(data):
    left_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))
    right_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))

    left = _frame_with_key(left_keys, "l_id")
    right = _frame_with_key(right_keys, "r_id")

    result = pandas.merge(left, right, how="inner", on="k")

    expected_pairs = {
        (left_id, right_id)
        for left_id, left_key in enumerate(left_keys)
        for right_id, right_key in enumerate(right_keys)
        if left_key == right_key
    }

    actual_pairs = {
        (int(row.l_id), int(row.r_id))
        for row in result.itertuples(index=False)
    }

    assert actual_pairs == expected_pairs


@given(st.data())
def test_pandas_merge_cross_product_property(data):
    left_values = data.draw(st.lists(st.integers(min_value=-10, max_value=10), min_size=0, max_size=5))
    right_values = data.draw(st.lists(st.text(min_size=0, max_size=3), min_size=0, max_size=5))

    left = pandas.DataFrame({"left_value": left_values})
    right = pandas.DataFrame({"right_value": right_values})

    result = pandas.merge(left, right, how="cross")

    expected_rows = [
        (left_value, right_value)
        for left_value in left_values
        for right_value in right_values
    ]

    actual_rows = list(result[["left_value", "right_value"]].itertuples(index=False, name=None))

    assert len(result) == len(left_values) * len(right_values)
    assert actual_rows == expected_rows


@given(st.data())
def test_pandas_merge_overlapping_columns_get_suffixes_property(data):
    left_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=5))
    right_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=5))
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = pandas.DataFrame(
        {
            "k": pandas.Series(left_keys, dtype="object"),
            "value": list(range(len(left_keys))),
            "left_only": list(range(100, 100 + len(left_keys))),
        }
    )
    right = pandas.DataFrame(
        {
            "k": pandas.Series(right_keys, dtype="object"),
            "value": list(range(len(right_keys))),
            "right_only": list(range(200, 200 + len(right_keys))),
        }
    )

    result = pandas.merge(left, right, how=how, on="k", suffixes=("_left", "_right"))

    assert list(result.columns) == ["k", "value_left", "left_only", "value_right", "right_only"]
    assert "value" not in result.columns
    assert "value_left" in result.columns
    assert "value_right" in result.columns


@given(st.data())
def test_pandas_merge_indicator_column_matches_row_origin_property(data):
    left_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))
    right_keys = data.draw(st.lists(_key_strategy, min_size=0, max_size=6))

    left = _frame_with_key(left_keys, "l_id")
    right = _frame_with_key(right_keys, "r_id")

    result = pandas.merge(left, right, how="outer", on="k", indicator=True)

    assert "_merge" in result.columns
    assert set(result["_merge"].astype(str)).issubset({"left_only", "right_only", "both"})

    for row in result.itertuples(index=False):
        has_left = not pandas.isna(row.l_id)
        has_right = not pandas.isna(row.r_id)

        if has_left and has_right:
            expected = "both"
        elif has_left:
            expected = "left_only"
        else:
            expected = "right_only"

        assert str(row._merge) == expected
# End program