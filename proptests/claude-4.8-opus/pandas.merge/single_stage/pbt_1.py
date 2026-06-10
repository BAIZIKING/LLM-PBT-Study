from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary:
# Generate two DataFrames each with a shared integer 'key' column drawn from a small
# domain (0-3) to guarantee overlapping/duplicate/non-matching keys, plus an overlapping
# 'val' column to exercise suffixing. Sizes include 0 (empty) up to several rows.
# We vary 'how' over inner/left/right/outer and check indicator consistency, row-count
# bounds per join type, suffix handling, and inner-join row-count commutativity.
@given(st.data())
def test_pandas_merge(data):
    # Small key domain so joins actually overlap, includes duplicates & gaps.
    key_strategy = st.lists(st.integers(min_value=0, max_value=3),
                            min_size=0, max_size=6)

    left_keys = data.draw(key_strategy, label="left_keys")
    right_keys = data.draw(key_strategy, label="right_keys")

    left = pd.DataFrame({
        "key": left_keys,
        "val": list(range(len(left_keys))),
    })
    right = pd.DataFrame({
        "key": right_keys,
        "val": list(range(100, 100 + len(right_keys))),
    })

    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]), label="how")

    # --- Perform the merge with indicator ---
    result = pd.merge(left, right, how=how, on="key", indicator=True)

    # ---- Property 1: overlapping column 'val' gets suffixed ----
    assert "val_x" in result.columns
    assert "val_y" in result.columns
    assert "val" not in result.columns  # the overlapping name should be gone
    assert "key" in result.columns

    # ---- Property 2: indicator consistency ----
    left_key_set = set(left_keys)
    right_key_set = set(right_keys)
    for _, row in result.iterrows():
        k = row["key"]
        merge_flag = row["_merge"]
        in_left = (not pd.isna(k)) and (k in left_key_set)
        in_right = (not pd.isna(k)) and (k in right_key_set)
        if merge_flag == "both":
            assert in_left and in_right
        elif merge_flag == "left_only":
            assert in_left and not in_right
        elif merge_flag == "right_only":
            assert in_right and not in_left

    # ---- Property 3: row count bounds depending on how ----
    from collections import Counter
    lc = Counter(left_keys)
    rc = Counter(right_keys)
    shared = set(lc) & set(rc)
    inner_count = sum(lc[k] * rc[k] for k in shared)

    n_result = len(result)

    if how == "inner":
        assert n_result == inner_count
    elif how == "left":
        # every left row contributes >=1 (1 if no match, else rc[k] matches)
        expected_left = sum(rc[k] if k in rc else 1 for k in left_keys)
        assert n_result == expected_left
        assert n_result >= len(left)
    elif how == "right":
        expected_right = sum(lc[k] if k in lc else 1 for k in right_keys)
        assert n_result == expected_right
        assert n_result >= len(right)
    elif how == "outer":
        # outer >= inner and includes union of keys
        assert n_result >= inner_count
        result_keys = set(result["key"].dropna().tolist())
        assert result_keys == (left_key_set | right_key_set)

    # ---- Property 4: inner-join row-count commutativity ----
    if how == "inner":
        reversed_result = pd.merge(right, left, how="inner", on="key")
        assert len(reversed_result) == n_result
# End program