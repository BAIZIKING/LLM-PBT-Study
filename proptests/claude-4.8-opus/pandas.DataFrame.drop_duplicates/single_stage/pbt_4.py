from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate small DataFrames drawn from a tiny value pool (ints + None) to
# force frequent duplicate rows, with a variable number of columns/rows. Randomly
# pick subset (None / single label / list of labels), keep ('first'/'last'/False),
# ignore_index and inplace. Verify: no duplicates remain, result rows are a subset
# of originals, the kept-count matches the expected semantics of keep, ignore_index
# relabels the index, and inplace mutates in place while returning None.
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    # Build columns from a tiny value pool to maximize duplicate likelihood.
    n_cols = data.draw(st.integers(min_value=1, max_value=4), label="n_cols")
    col_names = [f"c{i}" for i in range(n_cols)]
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")

    value_pool = st.sampled_from([0, 1, 2, None])
    columns_data = {}
    for name in col_names:
        columns_data[name] = data.draw(
            st.lists(value_pool, min_size=n_rows, max_size=n_rows),
            label=f"col_{name}",
        )
    df = pd.DataFrame(columns_data, columns=col_names)

    # Draw parameters.
    subset_kind = data.draw(st.sampled_from(["none", "single", "list"]), label="subset_kind")
    if subset_kind == "none":
        subset = None
    elif subset_kind == "single":
        subset = data.draw(st.sampled_from(col_names), label="subset_single")
    else:
        subset = data.draw(
            st.lists(st.sampled_from(col_names), min_size=1, max_size=n_cols, unique=True),
            label="subset_list",
        )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    ignore_index = data.draw(st.booleans(), label="ignore_index")
    inplace = data.draw(st.booleans(), label="inplace")

    # Reference (non-inplace) result for comparison.
    expected = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)

    if inplace:
        work = df.copy()
        ret = work.drop_duplicates(
            subset=subset, keep=keep, inplace=True, ignore_index=ignore_index
        )
        # Property: inplace returns None and mutates the frame to match expected.
        assert ret is None
        result = work
        pd.testing.assert_frame_equal(result, expected)
    else:
        result = expected

    # Normalize subset for pandas duplicated() call.
    dup_subset = subset

    # Property 1: No duplicate rows remain (considering subset).
    assert not result.duplicated(subset=dup_subset).any()

    # Property 2: Result is no larger than the original.
    assert len(result) <= len(df)

    # Property 3: Count semantics based on keep.
    # Determine grouping columns.
    if subset is None:
        group_cols = col_names
    elif isinstance(subset, str):
        group_cols = [subset]
    else:
        group_cols = list(subset)

    if len(df) == 0 or len(group_cols) == 0:
        n_unique = len(df)
    else:
        # Count unique combinations treating NaN as a distinct, stable group.
        filled = df[group_cols].astype(object).where(pd.notna(df[group_cols]), "<<NA>>")
        n_unique = len(filled.drop_duplicates())

    if keep in ("first", "last"):
        # One row kept per unique combination.
        assert len(result) == n_unique
    else:  # keep is False
        # Only combinations appearing exactly once survive.
        if len(df) == 0:
            expected_count = 0
        else:
            counts = filled.groupby(list(group_cols)).size()
            expected_count = int((counts == 1).sum())
        assert len(result) == expected_count

    # Property 4: ignore_index relabels the index to 0..n-1.
    if ignore_index:
        assert list(result.index) == list(range(len(result)))

    # Property 5: Every result row existed in the original (subset of rows).
    if len(result) > 0:
        orig_rows = df.astype(object).where(pd.notna(df), "<<NA>>")
        res_rows = result.astype(object).where(pd.notna(result), "<<NA>>")
        orig_set = set(map(tuple, orig_rows.to_numpy().tolist()))
        for row in map(tuple, res_rows.to_numpy().tolist()):
            assert row in orig_set
# End program