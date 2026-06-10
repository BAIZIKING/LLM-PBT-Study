from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate two DataFrames sharing a low-cardinality "key" column (drawn
# from a small domain including duplicates and None to force matches/non-matches
# and many-to-many cases), each with a non-overlapping value column and an
# overlapping "val" column (to exercise suffixes). Vary row counts (incl. empty),
# how, sort, indicator, and suffixes. Check row-count relationships between join
# types, indicator semantics, suffix application, return type, and key-set
# (union/intersection) semantics.
@given(st.data())
def test_pandas_merge(data):
    # --- Generate key domain (small, to force overlaps) ---
    key_domain = data.draw(
        st.lists(
            st.one_of(st.integers(min_value=0, max_value=5), st.just(None)),
            min_size=1, max_size=6, unique=True
        ),
        label="key_domain",
    )

    def make_df(prefix):
        n = data.draw(st.integers(min_value=0, max_value=6), label=f"{prefix}_n")
        keys = data.draw(
            st.lists(st.sampled_from(key_domain), min_size=n, max_size=n),
            label=f"{prefix}_keys",
        )
        return pd.DataFrame({
            "key": keys,
            f"{prefix}_only": list(range(n)),
            "val": list(range(100, 100 + n)),  # overlapping column for suffix test
        })

    left = make_df("left")
    right = make_df("right")

    how = data.draw(st.sampled_from(["inner", "left", "right", "outer"]), label="how")
    sort = data.draw(st.booleans(), label="sort")
    indicator = data.draw(st.booleans(), label="indicator")
    suffixes = data.draw(
        st.sampled_from([("_x", "_y"), ("_l", "_r"), ("_left", "_right")]),
        label="suffixes",
    )

    result = pd.merge(left, right, how=how, on="key",
                      sort=sort, indicator=indicator, suffixes=suffixes)

    # Property 4: return type is a DataFrame
    assert isinstance(result, pd.DataFrame)

    # Property 3: overlapping non-key column "val" must get the suffixes applied
    val_left = "val" + suffixes[0]
    val_right = "val" + suffixes[1]
    assert val_left in result.columns
    assert val_right in result.columns
    assert "val" not in result.columns  # original overlapping name should be gone

    # --- Compute join variants for row-count relationships ---
    r_inner = pd.merge(left, right, how="inner", on="key")
    r_left = pd.merge(left, right, how="left", on="key")
    r_right = pd.merge(left, right, how="right", on="key")
    r_outer = pd.merge(left, right, how="outer", on="key")

    # Property 1: inner is the intersection (smallest), outer is the union (largest)
    assert len(r_inner) <= len(r_left)
    assert len(r_inner) <= len(r_right)
    assert len(r_inner) <= len(r_outer)
    assert len(r_outer) >= len(r_left)
    assert len(r_outer) >= len(r_right)

    # Property 5: key-set semantics (treat NaN as a single comparable token)
    def key_set(df):
        return {("NA" if (x is None or (isinstance(x, float) and np.isnan(x))) else x)
                for x in df["key"].tolist()}

    left_keys = key_set(left)
    right_keys = key_set(right)
    # Per docs, null keys are matched against each other (non-SQL behavior),
    # so we treat NaN as a single comparable token above.
    assert key_set(r_outer) == (left_keys | right_keys)
    assert key_set(r_inner) == (left_keys & right_keys)

    # Property 2: indicator semantics
    if indicator:
        assert "_merge" in result.columns
        allowed = {"left_only", "right_only", "both"}
        actual = set(result["_merge"].astype(str).tolist())
        assert actual.issubset(allowed)
        if how == "inner":
            assert actual.issubset({"both"})
        elif how == "left":
            assert "right_only" not in actual
        elif how == "right":
            assert "left_only" not in actual
# End program