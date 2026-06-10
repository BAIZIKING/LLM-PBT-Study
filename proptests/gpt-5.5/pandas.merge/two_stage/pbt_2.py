from hypothesis import given, strategies as st
import pandas

_KEY_STRATEGY = st.lists(
    st.one_of(st.integers(min_value=-3, max_value=3), st.none()),
    min_size=0,
    max_size=6,
)


def _normalize_key(value):
    if pandas.isna(value):
        return ("__NULL__",)
    return ("__VALUE__", int(value))


def _counts(values):
    result = {}
    for value in values:
        key = _normalize_key(value)
        result[key] = result.get(key, 0) + 1
    return result


def _id_frame(keys, side):
    return pandas.DataFrame(
        {
            "key": pandas.Series(keys, dtype="object"),
            f"{side}_id": list(range(len(keys))),
        }
    )


@given(st.data())
def test_pandas_merge_overlapping_columns_are_suffixed(data):
    left_keys = data.draw(_KEY_STRATEGY, label="left_keys")
    right_keys = data.draw(_KEY_STRATEGY, label="right_keys")
    how = data.draw(
        st.sampled_from(["inner", "left", "right", "outer"]),
        label="how",
    )

    left = pandas.DataFrame(
        {
            "key": pandas.Series(left_keys, dtype="object"),
            "shared": list(range(len(left_keys))),
            "left_only": list(range(len(left_keys))),
        }
    )
    right = pandas.DataFrame(
        {
            "key": pandas.Series(right_keys, dtype="object"),
            "shared": list(range(len(right_keys))),
            "right_only": list(range(len(right_keys))),
        }
    )

    result = pandas.merge(
        left,
        right,
        how=how,
        on="key",
        suffixes=("_left", "_right"),
    )

    assert list(result.columns) == [
        "key",
        "shared_left",
        "left_only",
        "shared_right",
        "right_only",
    ]


@given(st.data())
def test_pandas_merge_matched_rows_have_equal_keys(data):
    left_keys = data.draw(_KEY_STRATEGY, label="left_keys")
    right_keys = data.draw(_KEY_STRATEGY, label="right_keys")
    how = data.draw(
        st.sampled_from(["inner", "left", "right", "outer"]),
        label="how",
    )

    left = _id_frame(left_keys, "left")
    right = _id_frame(right_keys, "right")

    result = pandas.merge(left, right, how=how, on="key")

    for _, row in result.iterrows():
        if pandas.notna(row["left_id"]) and pandas.notna(row["right_id"]):
            left_key = left_keys[int(row["left_id"])]
            right_key = right_keys[int(row["right_id"])]

            assert _normalize_key(left_key) == _normalize_key(right_key)
            assert _normalize_key(row["key"]) == _normalize_key(left_key)


@given(st.data())
def test_pandas_merge_output_key_set_matches_join_type(data):
    left_keys = data.draw(_KEY_STRATEGY, label="left_keys")
    right_keys = data.draw(_KEY_STRATEGY, label="right_keys")
    how = data.draw(
        st.sampled_from(["inner", "left", "right", "outer"]),
        label="how",
    )

    left = _id_frame(left_keys, "left")
    right = _id_frame(right_keys, "right")

    result = pandas.merge(left, right, how=how, on="key")

    left_set = {_normalize_key(value) for value in left_keys}
    right_set = {_normalize_key(value) for value in right_keys}
    result_set = {_normalize_key(value) for value in result["key"]}

    if how == "inner":
        expected_set = left_set & right_set
    elif how == "left":
        expected_set = left_set
    elif how == "right":
        expected_set = right_set
    else:
        expected_set = left_set | right_set

    assert result_set == expected_set


@given(st.data())
def test_pandas_merge_inner_multiplicity_is_product_of_duplicate_counts(data):
    left_keys = data.draw(_KEY_STRATEGY, label="left_keys")
    right_keys = data.draw(_KEY_STRATEGY, label="right_keys")

    left = _id_frame(left_keys, "left")
    right = _id_frame(right_keys, "right")

    result = pandas.merge(left, right, how="inner", on="key")

    left_counts = _counts(left_keys)
    right_counts = _counts(right_keys)
    result_counts = _counts(result["key"])

    expected_counts = {
        key: left_counts[key] * right_counts[key]
        for key in left_counts.keys() & right_counts.keys()
    }

    assert result_counts == expected_counts


@given(st.data())
def test_pandas_merge_cross_is_cartesian_product(data):
    left_values = data.draw(
        st.lists(st.integers(min_value=-100, max_value=100), min_size=0, max_size=6),
        label="left_values",
    )
    right_values = data.draw(
        st.lists(st.integers(min_value=-100, max_value=100), min_size=0, max_size=6),
        label="right_values",
    )

    left = pandas.DataFrame(
        {
            "left_id": list(range(len(left_values))),
            "left_value": left_values,
        }
    )
    right = pandas.DataFrame(
        {
            "right_id": list(range(len(right_values))),
            "right_value": right_values,
        }
    )

    result = pandas.merge(left, right, how="cross")

    expected_pairs = {
        (left_id, right_id)
        for left_id in range(len(left_values))
        for right_id in range(len(right_values))
    }
    actual_pairs = set(zip(result["left_id"], result["right_id"]))

    assert len(result) == len(left_values) * len(right_values)
    assert actual_pairs == expected_pairs
# End program