from hypothesis import given, strategies as st, settings, HealthCheck
import pandas as pd
import numpy as np

# Summary: Generate two DataFrames sharing a "key" column, with keys drawn from a
# small pool (to force matches, duplicates, and misses), plus value columns
# (including an overlapping column name to exercise suffixes). Randomly choose
# the merge parameters (how, sort, indicator). Verify return type, per-join-type
# row-count semantics, cross product size, indicator column validity, and that
# all expected keys appear for left/right/outer joins.
@given(st.data())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_pandas_merge():
    data = st.data()

    # --- Generate keys from a small pool to maximize matching/edge cases ---
    key_pool = data.draw(
        st.lists(st.integers(min_value=0, max_value=5), min_size=1, max_size=6),
        label="key_pool",
    )

    left_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=0, max_size=5),
        label="left_keys",
    )
    right_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=0, max_size=5),
        label="right_keys",
    )

    # Build DataFrames. Use an overlapping column "val" to test suffixes.
    left = pd.DataFrame({
        "key": left_keys,
        "val": list(range(len(left_keys))),
        "lonly": [x * 10 for x in range(len(left_keys))],
    })
    right = pd.DataFrame({
        "key": right_keys,
        "val": list(range(100, 100 + len(right_keys))),
        "ronly": [x * 100 for x in range(len(right_keys))],
    })

    how = data.draw(
        st.sampled_from(["left", "right", "outer", "inner", "cross"]),
        label="how",
    )
    sort = data.draw(st.booleans(), label="sort")
    indicator = data.draw(st.booleans(), label="indicator")

    # --- Perform merge ---
    if how == "cross":
        # cross merge does not allow merging on columns
        result = pd.merge(left, right, how="cross", sort=sort, indicator=indicator)
    else:
        result = pd.merge(left, right, how=how, on="key", sort=sort, indicator=indicator)

    # ----------------------- Property checks -----------------------

    # 1. Return type is always a DataFrame.
    assert isinstance(result, pd.DataFrame)

    # 2. Row-count semantics per join type.
    if how == "cross":
        # Cartesian product size.
        assert len(result) == len(left) * len(right)
        # All columns from both frames present (with suffixes on overlap).
        # Non-overlapping columns kept as-is.
        assert "lonly" in result.columns
        assert "ronly" in result.columns
        # overlapping non-key columns "key" and "val" get suffixes.
        assert "key_x" in result.columns and "key_y" in result.columns
        assert "val_x" in result.columns and "val_y" in result.columns
    else:
        ls = set(left_keys)
        rs = set(right_keys)

        if how == "inner":
            # Every key in result must appear in both frames.
            result_keys = set(result["key"].tolist())
            assert result_keys <= (ls & rs)
            # Row count equals sum over shared keys of (count_left * count_right).
            expected = 0
            for k in (ls & rs):
                cl = left_keys.count(k)
                cr = right_keys.count(k)
                expected += cl * cr
            assert len(result) == expected

        elif how == "left":
            # Every left key must appear in the result.
            result_keys = set(result["key"].tolist())
            assert ls <= result_keys
            # Each left row appears max(1, #right matches) times.
            expected = 0
            for k in left_keys:
                cr = right_keys.count(k)
                expected += max(1, cr)
            assert len(result) == expected

        elif how == "right":
            # Every right key must appear in the result.
            result_keys = set(result["key"].tolist())
            assert rs <= result_keys
            expected = 0
            for k in right_keys:
                cl = left_keys.count(k)
                expected += max(1, cl)
            assert len(result) == expected

        elif how == "outer":
            # Union of all keys must appear.
            result_keys = set(result["key"].tolist())
            assert (ls | rs) <= result_keys

        # The single join key column "key" is preserved (not suffixed)
        # because we merged on a common column.
        assert "key" in result.columns
        # Overlapping non-key column "val" gets suffixes.
        assert "val_x" in result.columns and "val_y" in result.columns

    # 3. Indicator column validity.
    if indicator:
        assert "_merge" in result.columns
        allowed = {"left_only", "right_only", "both"}
        assert set(result["_merge"].astype(str).unique()) <= allowed

# End program