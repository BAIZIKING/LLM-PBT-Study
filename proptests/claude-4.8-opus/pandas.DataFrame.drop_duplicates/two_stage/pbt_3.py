from hypothesis import given, strategies as st, settings
import pandas as pd


# Strategy for generating a DataFrame with a few columns and "duplicate-prone" values.
@st.composite
def dataframes(draw):
    n_cols = draw(st.integers(min_value=1, max_value=4))
    n_rows = draw(st.integers(min_value=0, max_value=30))

    col_names = [f"col{i}" for i in range(n_cols)]

    # Use a small pool of values per column so that duplicates are likely.
    def column_strategy():
        value_pool = draw(
            st.lists(
                st.one_of(
                    st.integers(min_value=-100, max_value=100),
                    st.text(alphabet="abc", min_size=0, max_size=2),
                    st.booleans(),
                ),
                min_size=1,
                max_size=4,
            )
        )
        return st.sampled_from(value_pool)

    data = {}
    for name in col_names:
        strat = column_strategy()
        data[name] = draw(st.lists(strat, min_size=n_rows, max_size=n_rows))

    return pd.DataFrame(data, columns=col_names)


def _row_tuples(df, cols):
    """Return list of tuples representing the values of df restricted to cols."""
    return [tuple(row) for row in df[cols].itertuples(index=False, name=None)]


def _all_row_tuples(df):
    return _row_tuples(df, list(df.columns))


@given(st.data())
@settings(max_examples=200)
def test_pandas_DataFrame_drop_duplicates_property(data):
    df = data.draw(dataframes())
    cols = list(df.columns)

    # Choose subset: None or a non-empty subset of columns.
    subset = data.draw(
        st.one_of(
            st.none(),
            st.lists(st.sampled_from(cols), min_size=1, max_size=len(cols), unique=True),
        )
    )
    keep = data.draw(st.sampled_from(["first", "last", False]))
    ignore_index = data.draw(st.booleans())
    inplace = data.draw(st.booleans())

    subset_cols = cols if subset is None else subset

    # Keep a snapshot of the original to compare against (since inplace mutates).
    original = df.copy(deep=True)
    original_index = list(original.index)
    original_subset_tuples = _row_tuples(original, subset_cols)
    original_full_tuples = _all_row_tuples(original)

    if inplace:
        ret = df.drop_duplicates(
            subset=subset, keep=keep, inplace=True, ignore_index=ignore_index
        )
        # Property 5 (inplace): returns None and df itself is modified.
        assert ret is None
        result = df
    else:
        result = df.drop_duplicates(
            subset=subset, keep=keep, inplace=False, ignore_index=ignore_index
        )
        # Property 5 (not inplace): original df unchanged.
        assert list(df.index) == original_index
        assert _all_row_tuples(df) == original_full_tuples

    # ---- Property 1: no duplicates remain w.r.t. subset per keep semantics ----
    result_subset_tuples = _row_tuples(result, subset_cols)
    if keep in ("first", "last"):
        # Every retained subset combination must be unique.
        assert len(result_subset_tuples) == len(set(result_subset_tuples))
    else:  # keep is False
        # Only combinations that appeared exactly once in the original remain.
        from collections import Counter

        orig_counts = Counter(original_subset_tuples)
        for t in result_subset_tuples:
            assert orig_counts[t] == 1

    # ---- Property 2: output rows are a subset of original rows ----
    result_full_tuples = _all_row_tuples(result)
    orig_full_counter_keys = set(original_full_tuples)
    for t in result_full_tuples:
        assert t in orig_full_counter_keys

    # ---- Property 3: number of rows in output ----
    from collections import Counter

    orig_subset_counts = Counter(original_subset_tuples)
    if keep in ("first", "last"):
        expected_n = len(orig_subset_counts)  # number of unique combinations
    else:
        expected_n = sum(1 for v in orig_subset_counts.values() if v == 1)
    assert len(result) == expected_n

    # ---- Property 4: keep='first'/'last' retain correct occurrence ----
    if not ignore_index and keep in ("first", "last"):
        # Map each subset combination to first/last original index.
        chosen_index = {}
        for idx, t in zip(original_index, original_subset_tuples):
            if keep == "first":
                if t not in chosen_index:
                    chosen_index[t] = idx
            else:  # last
                chosen_index[t] = idx
        expected_indices = sorted(chosen_index.values(), key=lambda x: original_index.index(x))
        # The set of result indices should equal the expected set of kept indices.
        assert set(result.index) == set(chosen_index.values())

    # ---- Property 5 (ignore_index) ----
    if ignore_index:
        assert list(result.index) == list(range(len(result)))
# End program