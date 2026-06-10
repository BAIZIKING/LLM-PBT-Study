from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate a DataFrame with a small value pool (to force duplicate rows),
# random number of rows/columns, plus random subset/keep/ignore_index/inplace params.
# Verify: idempotence, no remaining duplicates, result rows subset of original,
# non-increasing row count, ignore_index labeling, inplace consistency, and keep=False semantics.
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    # --- Build the DataFrame ---
    n_cols = data.draw(st.integers(min_value=1, max_value=4), label="n_cols")
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")
    col_names = [f"col{i}" for i in range(n_cols)]

    # Small value pool to encourage duplicate rows.
    value_strategy = st.sampled_from([0, 1, 2, "a", "b"])
    cols_data = {}
    for c in col_names:
        cols_data[c] = data.draw(
            st.lists(value_strategy, min_size=n_rows, max_size=n_rows),
            label=f"data_{c}",
        )
    df = pd.DataFrame(cols_data, columns=col_names)

    # --- Build parameters ---
    subset_choice = data.draw(
        st.sampled_from(["none", "single", "list"]), label="subset_choice"
    )
    if subset_choice == "none":
        subset = None
    elif subset_choice == "single":
        subset = data.draw(st.sampled_from(col_names), label="single_subset")
    else:
        subset = data.draw(
            st.lists(st.sampled_from(col_names), min_size=1, max_size=n_cols, unique=True),
            label="list_subset",
        )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    # The effective columns used for duplicate identification.
    if subset is None:
        eff_cols = list(col_names)
    elif isinstance(subset, list):
        eff_cols = subset
    else:
        eff_cols = [subset]

    # --- Call (inplace=False) ---
    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)
    assert result is not None

    # Property 4: non-increasing row count.
    assert len(result) <= len(df)

    # Property 2: no duplicates remain on the subset columns.
    assert not result.duplicated(subset=subset, keep="first").any()

    # Property 1: idempotence.
    result2 = result.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)
    assert result2.reset_index(drop=True).equals(result.reset_index(drop=True))

    # Property 3: every result row (on eff_cols) existed in original.
    orig_keys = set(map(tuple, df[eff_cols].itertuples(index=False, name=None)))
    res_keys = set(map(tuple, result[eff_cols].itertuples(index=False, name=None)))
    assert res_keys <= orig_keys

    # Property 5: ignore_index labeling.
    if ignore_index:
        assert list(result.index) == list(range(len(result)))

    # Property 7: keep=False removes all rows whose subset-key appears more than once.
    if keep is False:
        key_counts = df[eff_cols].groupby(eff_cols, dropna=False).size() if len(df) else None
        unique_keys = {k for k in orig_keys
                       if list(map(tuple, df[eff_cols].itertuples(index=False, name=None))).count(k) == 1}
        assert res_keys == unique_keys

    # Property 6: inplace consistency.
    df_copy = df.copy()
    ret = df_copy.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index, inplace=True)
    assert ret is None
    assert df_copy.reset_index(drop=True).equals(result.reset_index(drop=True))
# End program