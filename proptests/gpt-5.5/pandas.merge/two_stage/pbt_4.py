from hypothesis import given, strategies as st
import pandas


KEY = st.one_of(
    st.none(),
    st.text(alphabet="abc", min_size=0, max_size=3),
)
KEY_LIST = st.lists(KEY, min_size=0, max_size=6)


def normalize_key(key):
    if pandas.isna(key):
        return None
    return key


def keys_match(left_key, right_key):
    return normalize_key(left_key) == normalize_key(right_key)


def key_counts(keys):
    counts = {}
    for key in keys:
        normalized = normalize_key(key)
        counts[normalized] = counts.get(normalized, 0) + 1
    return counts


def make_frame(keys, id_column):
    return pandas.DataFrame(
        {
            "k": pandas.Series(keys, dtype=object),
            id_column: pandas.Series(
                [f"{id_column}_{i}" for i in range(len(keys))],
                dtype=object,
            ),
        }
    )


@given(st.data())
def test_pandas_merge_inner_rows_are_valid_equal_key_pairings(data):
    left_keys = data.draw(KEY_LIST)
    right_keys = data.draw(KEY_LIST)

    left = make_frame(left_keys, "left_id")
    right = make_frame(right_keys, "right_id")

    result = pandas.merge(left, right, how="inner", on="k")

    expected_pairs = []
    for left_index, left_key in enumerate(left_keys):
        for right_index, right_key in enumerate(right_keys):
            if keys_match(left_key, right_key):
                expected_pairs.append(
                    (f"left_id_{left_index}", f"right_id_{right_index}")
                )

    actual_pairs = list(zip(result["left_id"].tolist(), result["right_id"].tolist()))

    assert sorted(actual_pairs) == sorted(expected_pairs)


@given(st.data())
def test_pandas_merge_row_count_matches_join_multiplicity(data):
    left_keys = data.draw(KEY_LIST)
    right_keys = data.draw(KEY_LIST)
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = make_frame(left_keys, "left_id")
    right = make_frame(right_keys, "right_id")

    result = pandas.merge(left, right, how=how, on="k")

    left_counts = key_counts(left_keys)
    right_counts = key_counts(right_keys)
    all_keys = set(left_counts) | set(right_counts)

    expected_length = 0
    for key in all_keys:
        left_count = left_counts.get(key, 0)
        right_count = right_counts.get(key, 0)

        if how == "inner":
            expected_length += left_count * right_count
        elif how == "left":
            expected_length += left_count * right_count if right_count else left_count
        elif how == "right":
            expected_length += left_count * right_count if left_count else right_count
        elif how == "outer":
            if left_count and right_count:
                expected_length += left_count * right_count
            else:
                expected_length += left_count + right_count

    assert len(result) == expected_length


@given(st.data())
def test_pandas_merge_cross_is_cartesian_product(data):
    left_size = data.draw(st.integers(min_value=0, max_value=6))
    right_size = data.draw(st.integers(min_value=0, max_value=6))

    left = pandas.DataFrame(
        {
            "left_id": pandas.Series(
                [f"left_{i}" for i in range(left_size)],
                dtype=object,
            )
        }
    )
    right = pandas.DataFrame(
        {
            "right_id": pandas.Series(
                [f"right_{i}" for i in range(right_size)],
                dtype=object,
            )
        }
    )

    result = pandas.merge(left, right, how="cross")

    expected_pairs = [
        (f"left_{left_index}", f"right_{right_index}")
        for left_index in range(left_size)
        for right_index in range(right_size)
    ]
    actual_pairs = list(zip(result["left_id"].tolist(), result["right_id"].tolist()))

    assert len(result) == left_size * right_size
    assert actual_pairs == expected_pairs


@given(st.data())
def test_pandas_merge_overlapping_non_key_columns_are_suffixed(data):
    left_keys = data.draw(KEY_LIST)
    right_keys = data.draw(KEY_LIST)
    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]))

    left = pandas.DataFrame(
        {
            "k": pandas.Series(left_keys, dtype=object),
            "shared": pandas.Series(
                [f"left_shared_{i}" for i in range(len(left_keys))],
                dtype=object,
            ),
            "left_only": pandas.Series(
                [f"left_only_{i}" for i in range(len(left_keys))],
                dtype=object,
            ),
        }
    )
    right = pandas.DataFrame(
        {
            "k": pandas.Series(right_keys, dtype=object),
            "shared": pandas.Series(
                [f"right_shared_{i}" for i in range(len(right_keys))],
                dtype=object,
            ),
            "right_only": pandas.Series(
                [f"right_only_{i}" for i in range(len(right_keys))],
                dtype=object,
            ),
        }
    )

    result = pandas.merge(
        left,
        right,
        how=how,
        on="k",
        suffixes=("_left", "_right"),
    )

    assert list(result.columns) == [
        "k",
        "shared_left",
        "left_only",
        "shared_right",
        "right_only",
    ]
    assert "shared" not in result.columns


@given(st.data())
def test_pandas_merge_indicator_correctly_describes_row_source(data):
    left_keys = data.draw(KEY_LIST)
    right_keys = data.draw(KEY_LIST)

    left = make_frame(left_keys, "left_id")
    right = make_frame(right_keys, "right_id")

    result = pandas.merge(left, right, how="outer", on="k", indicator=True)

    left_key_set = {normalize_key(key) for key in left_keys}
    right_key_set = {normalize_key(key) for key in right_keys}

    observed_indicators = set(result["_merge"].astype(str).tolist())
    assert observed_indicators <= {"left_only", "right_only", "both"}

    for key, indicator in zip(result["k"].tolist(), result["_merge"].astype(str).tolist()):
        normalized = normalize_key(key)

        if normalized in left_key_set and normalized in right_key_set:
            expected = "both"
        elif normalized in left_key_set:
            expected = "left_only"
        else:
            expected = "right_only"

        assert indicator == expected


# End program