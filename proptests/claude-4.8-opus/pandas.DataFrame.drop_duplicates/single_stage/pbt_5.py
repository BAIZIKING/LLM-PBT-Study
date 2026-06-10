from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate small DataFrames over a tiny value domain (so duplicates appear),
# pick a random subset of real columns (None / single label / list), random keep
# ('first'/'last'/False), and random ignore_index. Check: result has no duplicates
# w.r.t. subset, result rows are a subset of original rows, the count matches the
# expected number of unique/once-only groups depending on keep, ignore_index produces
# a 0..n-1 index, and the operation is idempotent.
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    # Choose columns
    all_cols = ["a", "b", "c"]
    n_cols = data.draw(st.integers(min_value=1, max_value=3), label="n_cols")
    cols = all_cols[:n_cols]

    # Choose number of rows (allow empty)
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")

    # Small value domain to force duplicates
    cell = st.sampled_from([0, 1, 2, "x", "y"])
    df_dict = {
        col: data.draw(
            st.lists(cell, min_size=n_rows, max_size=n_rows), label=f"col_{col}"
        )
        for col in cols
    }
    df = pd.DataFrame(df_dict, columns=cols)

    # Choose subset: None, a single label, or a list of labels
    subset_choice = data.draw(
        st.one_of(
            st.none(),
            st.sampled_from(cols),
            st.lists(st.sampled_from(cols), min_size=1, max_size=len(cols), unique=True),
        ),
        label="subset",
    )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    result = df.drop_duplicates(
        subset=subset_choice, keep=keep, ignore_index=ignore_index
    )

    # Normalize subset into a list of columns for our own checks
    if subset_choice is None:
        subset_cols = list(cols)
    elif isinstance(subset_choice, list):
        subset_cols = subset_choice
    else:
        subset_cols = [subset_choice]

    # Property 1: no duplicates remain (w.r.t. subset) in the result
    assert not result.duplicated(subset=subset_cols, keep="first").any()

    # Property 2: every result row is a row that existed in the original
    # Compare full-row tuples (over all columns) as a multiset-subset check.
    orig_rows = [tuple(r) for r in df.to_numpy().tolist()]
    res_rows = [tuple(r) for r in result.to_numpy().tolist()]
    from collections import Counter
    orig_counter = Counter(orig_rows)
    res_counter = Counter(res_rows)
    for row, cnt in res_counter.items():
        assert orig_counter.get(row, 0) >= cnt

    # Property 3: expected number of rows depending on keep
    if df.shape[0] == 0:
        expected_n = 0
    elif keep is False:
        # rows whose subset-combination appears exactly once
        group_sizes = df.groupby(subset_cols, dropna=False).size() if subset_cols else None
        if subset_cols:
            expected_n = int((group_sizes == 1).sum())
        else:
            expected_n = 0
    else:
        # 'first' or 'last' keep exactly one per distinct subset-combination
        expected_n = int(df.drop_duplicates(subset=subset_cols).shape[0])
    assert result.shape[0] == expected_n

    # Property 4: ignore_index produces a 0..n-1 RangeIndex
    if ignore_index:
        assert list(result.index) == list(range(result.shape[0]))

    # Property 5: idempotence
    result2 = result.drop_duplicates(
        subset=subset_choice, keep=keep, ignore_index=ignore_index
    )
    if ignore_index:
        # indices already normalized; full equality should hold
        pd.testing.assert_frame_equal(result, result2)
    else:
        pd.testing.assert_frame_equal(result, result2)
# End program