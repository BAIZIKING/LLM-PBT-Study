from hypothesis import given, strategies as st, assume, settings
import pandas as pd
import numpy as np


# Strategy for generating "simple" hashable values that can be safely compared
# and won't overflow. We use small ints, bools, short strings, and None.
value_strategy = st.one_of(
    st.integers(min_value=-1000, max_value=1000),
    st.booleans(),
    st.text(alphabet="abcde", min_size=0, max_size=3),
    st.none(),
)


@st.composite
def dataframe_strategy(draw):
    """Generate a DataFrame with a small number of columns and rows,
    containing simple hashable values. We deliberately encourage duplicates
    by drawing from a small pool of values."""
    n_cols = draw(st.integers(min_value=1, max_value=4))
    n_rows = draw(st.integers(min_value=0, max_value=8))

    col_names = [f"col{i}" for i in range(n_cols)]

    data = {}
    for name in col_names:
        # Draw a small pool of values to encourage duplicate rows.
        pool = draw(st.lists(value_strategy, min_size=1, max_size=3))
        col = [draw(st.sampled_from(pool)) for _ in range(n_rows)]
        data[name] = col

    df = pd.DataFrame(data, columns=col_names)
    return df


def rows_as_tuples(df, cols=None):
    """Return a list of tuples representing rows (over given cols)."""
    if cols is None:
        cols = list(df.columns)
    if df.empty:
        return []
    return [tuple(row) for row in df[cols].itertuples(index=False, name=None)]


@given(st.data())
@settings(max_examples=300)
def test_pandas_DataFrame_drop_duplicates_property(data):
    df = data.draw(dataframe_strategy())

    cols = list(df.columns)

    # Choose subset: either None or a non-empty sublist of columns.
    subset_choice = data.draw(
        st.one_of(
            st.none(),
            st.lists(st.sampled_from(cols), min_size=1, max_size=len(cols), unique=True),
        )
    )
    keep = data.draw(st.sampled_from(["first", "last", False]))
    ignore_index = data.draw(st.booleans())

    effective_cols = cols if subset_choice is None else subset_choice

    result = df.drop_duplicates(
        subset=subset_choice, keep=keep, ignore_index=ignore_index
    )

    # ----- Property 1: idempotence / no duplicates in result -----
    result2 = result.drop_duplicates(
        subset=subset_choice, keep=keep, ignore_index=ignore_index
    )
    # Reset indexes for a fair comparison (drop_duplicates again may relabel
    # only when ignore_index, but values/order must be identical).
    assert result.reset_index(drop=True).equals(result2.reset_index(drop=True))

    # The result must have no duplicates over the effective columns.
    res_subset_tuples = rows_as_tuples(result, effective_cols)
    assert len(res_subset_tuples) == len(set(res_subset_tuples))

    # ----- Property 2: output is a subset of input rows -----
    input_full_tuples = rows_as_tuples(df, cols)
    result_full_tuples = rows_as_tuples(result, cols)
    # Each result row (full) must appear among input rows.
    from collections import Counter
    input_counter = Counter(input_full_tuples)
    result_counter = Counter(result_full_tuples)
    for row, count in result_counter.items():
        assert row in input_counter
        assert count <= input_counter[row]
    assert len(result) <= len(df)

    # ----- Property 3: order preserved, same columns -----
    assert list(result.columns) == list(df.columns)
    # Order preservation: the result full-rows must appear in the same relative
    # order as a filtered version of the original rows.
    # Build expected retained rows by manual computation below (property 4),
    # which also validates ordering.

    # ----- Property 4: correct rows retained per keep semantics -----
    # Compute expected retained positional indices manually.
    subset_tuples = rows_as_tuples(df, effective_cols)
    n = len(subset_tuples)

    if keep == "first":
        seen = set()
        expected_positions = []
        for i, t in enumerate(subset_tuples):
            if t not in seen:
                seen.add(t)
                expected_positions.append(i)
    elif keep == "last":
        seen = set()
        expected_positions = []
        for i in range(n - 1, -1, -1):
            t = subset_tuples[i]
            if t not in seen:
                seen.add(t)
                expected_positions.append(i)
        expected_positions.reverse()
    else:  # keep is False
        counts = Counter(subset_tuples)
        expected_positions = [i for i, t in enumerate(subset_tuples) if counts[t] == 1]

    expected_full_rows = [rows_as_tuples(df, cols)[i] for i in expected_positions]
    assert result_full_tuples == expected_full_rows

    # ----- Property 5: index behavior and inplace -----
    if ignore_index:
        assert list(result.index) == list(range(len(result)))
    else:
        original_index = list(df.index)
        expected_index_labels = [original_index[i] for i in expected_positions]
        assert list(result.index) == expected_index_labels

    # inplace=True returns None and mutates a copy to equal non-inplace result.
    df_copy = df.copy(deep=True)
    ret = df_copy.drop_duplicates(
        subset=subset_choice, keep=keep, inplace=True, ignore_index=ignore_index
    )
    assert ret is None
    assert df_copy.reset_index(drop=True).equals(result.reset_index(drop=True))
    if not ignore_index:
        assert list(df_copy.index) == list(result.index)
# End program