from hypothesis import given, strategies as st, settings
import pandas as pd

# Strategy for generating "cell" values that are hashable, comparable for equality,
# and avoid problematic float behavior (NaN != NaN). We restrict to small ints,
# short strings, and booleans to keep duplicates likely and avoid overflow issues.
cell_values = st.one_of(
    st.integers(min_value=-100, max_value=100),
    st.text(alphabet="abc", min_size=0, max_size=3),
    st.booleans(),
)


@st.composite
def dataframes(draw):
    # Choose number of columns and their names.
    n_cols = draw(st.integers(min_value=1, max_value=4))
    col_names = [f"col{i}" for i in range(n_cols)]

    # Choose number of rows.
    n_rows = draw(st.integers(min_value=0, max_value=20))

    # Build the data column by column.
    data = {}
    for name in col_names:
        data[name] = draw(
            st.lists(cell_values, min_size=n_rows, max_size=n_rows)
        )

    df = pd.DataFrame(data, columns=col_names)
    return df


@st.composite
def df_and_args(draw):
    df = draw(dataframes())
    cols = list(df.columns)

    # subset: either None, or a non-empty subset of the columns.
    use_subset = draw(st.booleans())
    if use_subset and len(cols) > 0:
        subset = draw(
            st.lists(st.sampled_from(cols), min_size=1, max_size=len(cols), unique=True)
        )
    else:
        subset = None

    keep = draw(st.sampled_from(["first", "last", False]))
    ignore_index = draw(st.booleans())

    return df, subset, keep, ignore_index


@settings(max_examples=300)
@given(df_and_args())
def test_pandas_DataFrame_drop_duplicates_property(args):
    df, subset, keep, ignore_index = args

    result = df.drop_duplicates(
        subset=subset, keep=keep, ignore_index=ignore_index
    )

    considered = list(df.columns) if subset is None else subset

    # --- Property 1: No duplicate rows remain (per keep semantics). ---
    if keep in ("first", "last"):
        # No duplicates in the considered columns within the result.
        assert not result.duplicated(subset=subset).any()
    else:  # keep is False
        # All rows that had duplicates in the original (over considered columns)
        # must be entirely absent. The remaining ones each appeared exactly once.
        orig_counts = df.groupby(considered, dropna=False).size() if len(df) > 0 else None
        # Every kept row's combination must have appeared exactly once originally.
        for _, row in result[considered].iterrows():
            key = tuple(row.tolist())
            count = (df[considered].apply(tuple, axis=1) == key).sum() if len(df) > 0 else 0
            assert count == 1

    # --- Property 2: Output is a subset of input rows; columns unchanged. ---
    assert list(result.columns) == list(df.columns)
    orig_rows = [tuple(r) for r in df.to_numpy().tolist()]
    for r in result.to_numpy().tolist():
        assert tuple(r) in orig_rows

    # --- Property 3: Output size bounded and consistent with uniqueness. ---
    assert len(result) <= len(df)
    if len(df) == 0:
        assert len(result) == 0
    else:
        combo_counts = df[considered].apply(tuple, axis=1).value_counts()
        if keep in ("first", "last"):
            assert len(result) == len(combo_counts)
        else:  # keep is False
            assert len(result) == int((combo_counts == 1).sum())

    # --- Property 4: keep='first'/'last' preserve correct occurrences. ---
    if keep in ("first", "last") and len(df) > 0:
        # Recompute the expected kept original-index for each considered-combination.
        combo_series = df[considered].apply(tuple, axis=1)
        # Map combination -> expected original positional index.
        grouped = {}
        for pos, key in enumerate(combo_series.tolist()):
            if keep == "first":
                if key not in grouped:
                    grouped[key] = pos
            else:  # last
                grouped[key] = pos
        expected_positions = sorted(grouped.values())
        # The full rows kept should correspond exactly to those original positions.
        expected_rows = [tuple(df.iloc[p].tolist()) for p in expected_positions]
        actual_rows = [tuple(r) for r in result.to_numpy().tolist()]
        assert actual_rows == expected_rows

    # --- Property 5: ignore_index controls index labeling. ---
    if ignore_index:
        assert list(result.index) == list(range(len(result)))
    else:
        # Index labels must be the original labels of the kept rows.
        # The kept rows correspond to a subsequence of the original index.
        orig_index = list(df.index)
        result_index = list(result.index)
        # Each result index label must exist in original index.
        for lbl in result_index:
            assert lbl in orig_index
        # And they must appear in the same relative order as in the original.
        positions = [orig_index.index(lbl) for lbl in result_index]
        assert positions == sorted(positions)
# End program