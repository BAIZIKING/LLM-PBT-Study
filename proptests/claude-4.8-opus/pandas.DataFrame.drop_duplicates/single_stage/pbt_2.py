from hypothesis import given, settings, strategies as st
import pandas as pd

# Summary: Generate a small DataFrame from a tiny value pool (so duplicate rows
# arise often), with random number of rows/cols (including empty). Randomly pick
# subset (None / single label / list of labels), keep ('first'/'last'/False),
# and ignore_index. Verify: output rows are a subset of input rows, no remaining
# duplicates per subset (or full removal when keep=False), idempotence,
# first/last yield same count, ignore_index relabels, and inplace returns None
# while mutating equivalently.
@given(st.data())
@settings(max_examples=200)
def test_pandas_DataFrame_drop_duplicates(data):
    n_cols = data.draw(st.integers(min_value=1, max_value=3), label="n_cols")
    columns = [f"c{i}" for i in range(n_cols)]
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")

    # small value pool to encourage duplicate rows
    value_pool = [0, 1, 2, "a", "b", None]
    cell = st.sampled_from(value_pool)

    rows = [
        data.draw(st.lists(cell, min_size=n_cols, max_size=n_cols), label=f"row_{r}")
        for r in range(n_rows)
    ]
    df = pd.DataFrame(rows, columns=columns) if n_rows > 0 else pd.DataFrame(columns=columns)

    # choose subset
    subset_choice = data.draw(
        st.sampled_from(["none", "single", "list"]), label="subset_choice"
    )
    if subset_choice == "none":
        subset = None
    elif subset_choice == "single":
        subset = data.draw(st.sampled_from(columns), label="single_subset")
    else:
        subset = data.draw(
            st.lists(st.sampled_from(columns), min_size=1, max_size=n_cols, unique=True),
            label="list_subset",
        )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)

    # Determine the subset columns actually used
    if subset is None:
        used_cols = columns
    elif isinstance(subset, list):
        used_cols = subset
    else:
        used_cols = [subset]

    # --- Property 1: result rows are a subset of original rows ---
    # Compare on used columns; every kept combination must have existed.
    def to_tuples(frame):
        return [tuple(rec) for rec in frame[used_cols].to_numpy().tolist()]

    orig_subset_tuples = to_tuples(df)
    res_subset_tuples = to_tuples(result)
    for t in res_subset_tuples:
        assert t in orig_subset_tuples

    # --- Property 2: no remaining duplicates per subset ---
    if keep in ("first", "last"):
        assert len(res_subset_tuples) == len(set(res_subset_tuples))
        # set of unique subset-combos preserved
        assert set(res_subset_tuples) == set(orig_subset_tuples)
    else:  # keep is False -> drop all rows whose subset-combo was duplicated
        from collections import Counter
        counts = Counter(orig_subset_tuples)
        expected = {t for t, c in counts.items() if c == 1}
        assert set(res_subset_tuples) == expected
        assert len(res_subset_tuples) == len(set(res_subset_tuples))

    # --- Property 3: idempotence ---
    again = result.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)
    pd.testing.assert_frame_equal(
        again.reset_index(drop=True), result.reset_index(drop=True)
    )

    # --- Property 4: first vs last yield same number of kept rows ---
    res_first = df.drop_duplicates(subset=subset, keep="first")
    res_last = df.drop_duplicates(subset=subset, keep="last")
    assert len(res_first) == len(res_last)

    # --- Property 5: ignore_index relabels to RangeIndex ---
    if ignore_index:
        assert list(result.index) == list(range(len(result)))

    # --- Property 6: inplace=True returns None and mutates equivalently ---
    df_copy = df.copy()
    ret = df_copy.drop_duplicates(
        subset=subset, keep=keep, inplace=True, ignore_index=ignore_index
    )
    assert ret is None
    pd.testing.assert_frame_equal(
        df_copy.reset_index(drop=True), result.reset_index(drop=True)
    )
# End program