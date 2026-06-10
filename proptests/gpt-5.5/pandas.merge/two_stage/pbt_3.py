from hypothesis import given, strategies as st
import pandas


def _normalize_key(value):
    if pandas.isna(value):
        return ("__NULL__",)
    return ("__VALUE__", value)


def _counts(values):
    result = {}
    for value in values:
        key = _normalize_key(value)
        result[key] = result.get(key, 0) + 1
    return result


def _frame_with_key(keys, payload_name, payload_prefix):
    return pandas.DataFrame(
        {
            "k": pandas.Series(keys, dtype="object"),
            payload_name: pandas.Series(
                [f"{payload_prefix}{i}" for i in range(len(keys))],
                dtype="object",
            ),
        }
    )


def _small_keys():
    return st.lists(
        st.one_of(st.integers(min_value=-3, max_value=3), st.none()),
        min_size=0,
        max_size=6,
    )


@given(st.data())
def test_pandas_merge_row_count_matches_join_multiplicity(data):
    left_keys = data.draw(_small_keys())
    right_keys = data.draw(_small_keys())
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = _frame_with_key(left_keys, "lv", "L")
    right = _frame_with_key(right_keys, "rv", "R")

    result = pandas.merge(left, right, how=how, on="k")

    left_counts = _counts(left_keys)
    right_counts = _counts(right_keys)
    all_keys = set(left_counts) | set(right_counts)

    if how == "inner":
        expected_rows = sum(
            left_counts[key] * right_counts[key]
            for key in all_keys
            if key in left_counts and key in right_counts
        )
    elif how == "left":
        expected_rows = sum(
            left_counts[key] * max(right_counts.get(key, 0), 1)
            for key in left_counts
        )
    elif how == "right":
        expected_rows = sum(
            right_counts[key] * max(left_counts.get(key, 0), 1)
            for key in right_counts
        )
    else:
        expected_rows = sum(
            left_counts.get(key, 0) * right_counts.get(key, 0)
            if key in left_counts and key in right_counts
            else left_counts.get(key, 0) + right_counts.get(key, 0)
            for key in all_keys
        )

    assert len(result) == expected_rows


@given(st.data())
def test_pandas_merge_rows_have_valid_provenance_and_matching_keys(data):
    left_keys = data.draw(_small_keys())
    right_keys = data.draw(_small_keys())

    left = _frame_with_key(left_keys, "li", "L")
    right = _frame_with_key(right_keys, "ri", "R")

    result = pandas.merge(left, right, how="outer", on="k", indicator=True)

    left_by_id = {f"L{i}": _normalize_key(key) for i, key in enumerate(left_keys)}
    right_by_id = {f"R{i}": _normalize_key(key) for i, key in enumerate(right_keys)}
    right_key_set = set(right_by_id.values())
    left_key_set = set(left_by_id.values())

    for _, row in result.iterrows():
        row_key = _normalize_key(row["k"])

        if row["_merge"] == "both":
            assert row["li"] in left_by_id
            assert row["ri"] in right_by_id
            assert left_by_id[row["li"]] == row_key
            assert right_by_id[row["ri"]] == row_key
            assert left_by_id[row["li"]] == right_by_id[row["ri"]]

        elif row["_merge"] == "left_only":
            assert row["li"] in left_by_id
            assert pandas.isna(row["ri"])
            assert left_by_id[row["li"]] == row_key
            assert row_key not in right_key_set

        elif row["_merge"] == "right_only":
            assert pandas.isna(row["li"])
            assert row["ri"] in right_by_id
            assert right_by_id[row["ri"]] == row_key
            assert row_key not in left_key_set

        else:
            assert False


@given(st.data())
def test_pandas_merge_output_schema_suffixes_and_indicator(data):
    left_keys = data.draw(_small_keys())
    right_keys = data.draw(_small_keys())
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = pandas.DataFrame(
        {
            "k": pandas.Series(left_keys, dtype="object"),
            "value": pandas.Series(range(len(left_keys)), dtype="int64"),
            "left_only": pandas.Series([f"L{i}" for i in range(len(left_keys))], dtype="object"),
        }
    )
    right = pandas.DataFrame(
        {
            "k": pandas.Series(right_keys, dtype="object"),
            "value": pandas.Series(range(len(right_keys)), dtype="int64"),
            "right_only": pandas.Series([f"R{i}" for i in range(len(right_keys))], dtype="object"),
        }
    )

    result = pandas.merge(
        left,
        right,
        how=how,
        on="k",
        suffixes=("_left", "_right"),
        indicator="source",
    )

    assert list(result.columns) == [
        "k",
        "value_left",
        "left_only",
        "value_right",
        "right_only",
        "source",
    ]
    assert set(result["source"].cat.categories) == {"left_only", "right_only", "both"}


@given(st.data())
def test_pandas_merge_preserves_left_row_order_for_left_and_inner_joins(data):
    left_keys = data.draw(_small_keys())
    right_keys = data.draw(_small_keys())
    how = data.draw(st.sampled_from(["left", "inner"]))

    left = pandas.DataFrame(
        {
            "k": pandas.Series(left_keys, dtype="object"),
            "left_position": pandas.Series(range(len(left_keys)), dtype="int64"),
        }
    )
    right = pandas.DataFrame(
        {
            "k": pandas.Series(right_keys, dtype="object"),
            "right_position": pandas.Series(range(len(right_keys)), dtype="int64"),
        }
    )

    result = pandas.merge(left, right, how=how, on="k")

    positions = list(result["left_position"])
    assert positions == sorted(positions)


@given(st.data())
def test_pandas_merge_cross_join_is_cartesian_product(data):
    left_size = data.draw(st.integers(min_value=0, max_value=6))
    right_size = data.draw(st.integers(min_value=0, max_value=6))

    left = pandas.DataFrame({"left_id": list(range(left_size))})
    right = pandas.DataFrame({"right_id": list(range(right_size))})

    result = pandas.merge(left, right, how="cross")

    assert len(result) == left_size * right_size

    actual_pairs = list(zip(result["left_id"], result["right_id"]))
    expected_pairs = [
        (left_id, right_id)
        for left_id in range(left_size)
        for right_id in range(right_size)
    ]

    assert actual_pairs == expected_pairs


# End program