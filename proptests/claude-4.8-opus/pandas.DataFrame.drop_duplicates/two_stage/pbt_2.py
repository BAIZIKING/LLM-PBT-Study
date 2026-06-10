from hypothesis import given, strategies as st, settings
import pandas as pd


# Strategy for building a DataFrame with a few columns and small repeated-value
# domains so that duplicates actually appear frequently.
def dataframe_strategy(draw):
    n_cols = draw(st.integers(min_value=1, max_value=4))
    n_rows = draw(st.integers(min_value=0, max_value=30))
    col_names = [f"col{i}" for i in range(n_cols)]

    # Use small value domains to encourage duplicates.
    value_strategy = st.one_of(
        st.integers(min_value=-5, max_value=5),
        st.sampled_from(["a", "b", "c"]),
    )

    data = {}
    for name in col_names:
        col = draw(st.lists(value_strategy, min_size=n_rows, max_size=n_rows))
        data[name] = col

    df = pd.DataFrame(data, columns=col_names)
    return df


@given(st.data())
@settings(max_examples=200)
def test_pandas_DataFrame_drop_duplicates_property(data):
    df = data.draw(st.builds(lambda d: dataframe_strategy(d), st.data())) \
        if False else data.draw(st.builds(dataframe_strategy, st.just(None))) \
        if False else None

    # Build the DataFrame directly using the helper with the data() object.
    df = dataframe_strategy(data)

    cols = list(df.columns)

    # Choose subset: either None or a non-empty subset of the columns.
    if cols:
        subset = data.draw(
            st.one_of(
                st.none(),
                st.lists(st.sampled_from(cols), min_size=1, max_size=len(cols),
                         unique=True),
            )
        )
    else:
        subset = None

    keep = data.draw(st.sampled_from(["first", "last", False]))
    ignore_index = data.draw(st.booleans())
    inplace = data.draw(st.booleans())

    subset_cols = cols if subset is None else subset

    # Keep a pristine copy of the original for comparisons.
    df_original = df.copy(deep=True)

    if inplace:
        df_work = df.copy(deep=True)
        result = df_work.drop_duplicates(
            subset=subset, keep=keep, ignore_index=ignore_index, inplace=True
        )
        # Property 4 (inplace branch): returns None.
        assert result is None
        out = df_work
    else:
        out = df.drop_duplicates(
            subset=subset, keep=keep, ignore_index=ignore_index, inplace=False
        )
        # Property 4 (non-inplace branch): returns a DataFrame and original unmodified.
        assert isinstance(out, pd.DataFrame)
        pd.testing.assert_frame_equal(df, df_original)

    # ----- Property 1: no duplicates remain according to keep rule -----
    if subset_cols:
        counts = out[subset_cols].value_counts(dropna=False) if len(out) else None
        if keep is False:
            # No subset-combination appears more than once; additionally any
            # combination that appeared >1 time in the input must be absent.
            if len(out):
                assert (counts <= 1).all()
            orig_counts = df_original[subset_cols].value_counts(dropna=False)
            dup_combos = set(orig_counts[orig_counts > 1].index)
            out_combos = set(out[subset_cols].value_counts(dropna=False).index) \
                if len(out) else set()
            assert dup_combos.isdisjoint(out_combos)
        else:
            if len(out):
                assert (counts <= 1).all()
    else:
        # No columns at all -> result must equal input (no duplicates possible).
        pass

    # ----- Property 2: output rows are a subset of input rows -----
    # Compare on a value basis (ignoring index). Every output row tuple must
    # exist among the input row tuples.
    input_row_tuples = [tuple(r) for r in df_original.to_numpy().tolist()]
    from collections import Counter
    input_counter = Counter(input_row_tuples)
    for r in out.to_numpy().tolist():
        assert tuple(r) in input_counter

    # ----- Property 5: index behaviour -----
    if ignore_index:
        assert list(out.index) == list(range(len(out)))
    else:
        # Each output index label must come from original index labels,
        # and indices must be unique (since drop_duplicates keeps distinct rows).
        for idx in out.index:
            assert idx in set(df_original.index)

    # ----- Property 3: first/last occurrence semantics -----
    # Recompute the expected retained original-index positions and compare values.
    if not ignore_index and subset_cols and len(df_original):
        # Determine expected kept positions using the documented semantics.
        if keep == "first":
            expected = df_original.drop_duplicates(subset=subset, keep="first")
        elif keep == "last":
            expected = df_original.drop_duplicates(subset=subset, keep="last")
        else:
            expected = df_original.drop_duplicates(subset=subset, keep=False)

        # Compare index labels and full row contents.
        assert list(out.index) == list(expected.index)
        pd.testing.assert_frame_equal(
            out.reset_index(drop=True), expected.reset_index(drop=True)
        )
# End program