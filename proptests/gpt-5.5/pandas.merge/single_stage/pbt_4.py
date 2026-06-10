from hypothesis import given, strategies as st
import numpy as np
import pandas as pd
from collections import Counter

# Summary: Generate small left/right DataFrames with duplicate keys, missing keys, empty inputs,
# overlapping non-key columns, different join-key styles (`on`, `left_on`/`right_on`, index joins),
# all merge modes including `cross`, varied `sort`, `copy`, `suffixes`, `indicator`, and valid
# `validate` settings. Check independently-computed row cardinality, pandas' documented null-key
# matching behavior, indicator source counts, and suffix handling for overlapping columns.
@given(st.data())
def test_pandas_merge(data):
    key_values = st.one_of(st.integers(-2, 2).map(float), st.just(np.nan))

    def norm_key(x):
        return ("<NA>",) if pd.isna(x) else ("<VALUE>", x)

    def counts(keys):
        return Counter(norm_key(k) for k in keys)

    def suffixed(name, suffix):
        return name if suffix is None else f"{name}{suffix}"

    left_n = data.draw(st.integers(min_value=0, max_value=5), label="left_n")
    right_n = data.draw(st.integers(min_value=0, max_value=5), label="right_n")

    left_keys = data.draw(
        st.lists(key_values, min_size=left_n, max_size=left_n),
        label="left_keys",
    )
    right_keys = data.draw(
        st.lists(key_values, min_size=right_n, max_size=right_n),
        label="right_keys",
    )

    left = pd.DataFrame(
        {
            "shared": data.draw(
                st.lists(st.integers(-100, 100), min_size=left_n, max_size=left_n),
                label="left_shared",
            ),
            "lval": data.draw(
                st.lists(st.integers(-100, 100), min_size=left_n, max_size=left_n),
                label="lval",
            ),
        }
    )
    right = pd.DataFrame(
        {
            "shared": data.draw(
                st.lists(st.integers(-100, 100), min_size=right_n, max_size=right_n),
                label="right_shared",
            ),
            "rval": data.draw(
                st.lists(st.integers(-100, 100), min_size=right_n, max_size=right_n),
                label="rval",
            ),
        }
    )

    how = data.draw(
        st.sampled_from(["inner", "left", "right", "outer", "cross"]),
        label="how",
    )

    merge_kwargs = {}
    if how != "cross":
        join_style = data.draw(
            st.sampled_from(["on", "left_right_on", "index"]),
            label="join_style",
        )

        if join_style == "on":
            left.insert(0, "key", left_keys)
            right.insert(0, "key", right_keys)
            merge_kwargs["on"] = "key"
        elif join_style == "left_right_on":
            left.insert(0, "lkey", left_keys)
            right.insert(0, "rkey", right_keys)
            merge_kwargs["left_on"] = "lkey"
            merge_kwargs["right_on"] = "rkey"
        else:
            left.index = pd.Index(left_keys, name="join_key")
            right.index = pd.Index(right_keys, name="join_key")
            merge_kwargs["left_index"] = True
            merge_kwargs["right_index"] = True

    suffixes = data.draw(
        st.sampled_from(
            [
                ("_x", "_y"),
                ("_left", "_right"),
                (None, "_right"),
                ("_left", None),
            ]
        ),
        label="suffixes",
    )
    sort = data.draw(st.booleans(), label="sort")
    copy = data.draw(st.one_of(st.none(), st.booleans()), label="copy")
    indicator = data.draw(st.sampled_from([False, True, "source"]), label="indicator")

    left_counts = counts(left_keys)
    right_counts = counts(right_keys)
    left_unique = all(v <= 1 for v in left_counts.values())
    right_unique = all(v <= 1 for v in right_counts.values())

    validate_choices = [None, "m:m", "many_to_many"]
    if how != "cross":
        if left_unique and right_unique:
            validate_choices.extend(["1:1", "one_to_one"])
        if left_unique:
            validate_choices.extend(["1:m", "one_to_many"])
        if right_unique:
            validate_choices.extend(["m:1", "many_to_one"])

    validate = data.draw(st.sampled_from(validate_choices), label="validate")

    result = pd.merge(
        left,
        right,
        how=how,
        sort=sort,
        suffixes=suffixes,
        copy=copy,
        indicator=indicator,
        validate=validate,
        **merge_kwargs,
    )

    assert suffixed("shared", suffixes[0]) in result.columns
    assert suffixed("shared", suffixes[1]) in result.columns

    if how == "cross":
        expected_both = left_n * right_n
        expected_left_only = 0
        expected_right_only = 0
        expected_rows = expected_both
    else:
        left_key_set = set(left_counts)
        right_key_set = set(right_counts)
        common_keys = left_key_set & right_key_set

        expected_both = sum(left_counts[k] * right_counts[k] for k in common_keys)
        expected_left_only = sum(left_counts[k] for k in left_key_set - right_key_set)
        expected_right_only = sum(right_counts[k] for k in right_key_set - left_key_set)

        if how == "inner":
            expected_rows = expected_both
            expected_left_only = 0
            expected_right_only = 0
        elif how == "left":
            expected_rows = expected_both + expected_left_only
            expected_right_only = 0
        elif how == "right":
            expected_rows = expected_both + expected_right_only
            expected_left_only = 0
        else:
            expected_rows = expected_both + expected_left_only + expected_right_only

    assert len(result) == expected_rows

    if indicator:
        indicator_name = "_merge" if indicator is True else indicator
        assert indicator_name in result.columns

        observed = result[indicator_name].value_counts().to_dict()
        assert observed.get("both", 0) == expected_both
        assert observed.get("left_only", 0) == expected_left_only
        assert observed.get("right_only", 0) == expected_right_only
        assert set(result[indicator_name].dropna().astype(str)).issubset(
            {"left_only", "right_only", "both"}
        )
# End program