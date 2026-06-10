from hypothesis import given, strategies as st, settings
import pandas as pd
import numpy as np
import math

# Summary: Generate DataFrames with random shapes and mixed dtype columns
# (ints, floats with possible NaN, strings, bools). Then randomly pick a
# subset of columns to sort `by`, with random `ascending` (bool or list),
# `na_position`, `kind`, `ignore_index`, and an optional vectorized `key`.
# Verify shape preservation, row-multiset preservation, monotonicity of the
# primary sort column, na_position placement, ignore_index relabeling, and
# unchanged columns.
@given(st.data())
@settings(max_examples=300)
def test_pandas_DataFrame_sort_values(data):
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")
    n_cols = data.draw(st.integers(min_value=1, max_value=4), label="n_cols")

    col_names = [f"col{i}" for i in range(n_cols)]

    # Column value strategies (per-column dtype choice)
    def make_column():
        kind = data.draw(st.sampled_from(["int", "float", "str", "bool"]),
                         label="col_kind")
        if kind == "int":
            return data.draw(st.lists(st.integers(min_value=-50, max_value=50),
                                      min_size=n_rows, max_size=n_rows))
        elif kind == "float":
            return data.draw(st.lists(
                st.one_of(
                    st.floats(min_value=-100, max_value=100,
                              allow_nan=False, allow_infinity=False),
                    st.just(float("nan")),
                ),
                min_size=n_rows, max_size=n_rows))
        elif kind == "str":
            return data.draw(st.lists(
                st.text(alphabet="abcABC", min_size=0, max_size=3),
                min_size=n_rows, max_size=n_rows))
        else:  # bool
            return data.draw(st.lists(st.booleans(),
                                      min_size=n_rows, max_size=n_rows))

    df_dict = {name: make_column() for name in col_names}
    df = pd.DataFrame(df_dict, columns=col_names)

    # Choose 'by': a non-empty subset of columns (order matters)
    by_size = data.draw(st.integers(min_value=1, max_value=n_cols), label="by_size")
    by = data.draw(st.permutations(col_names), label="by_perm")[:by_size]

    # ascending: single bool or list of bools matching len(by)
    use_list_asc = data.draw(st.booleans(), label="use_list_asc")
    if use_list_asc:
        ascending = data.draw(
            st.lists(st.booleans(), min_size=len(by), max_size=len(by)),
            label="ascending_list")
    else:
        ascending = data.draw(st.booleans(), label="ascending_bool")

    na_position = data.draw(st.sampled_from(["first", "last"]), label="na_position")
    kind = data.draw(st.sampled_from(["quicksort", "mergesort", "heapsort", "stable"]),
                     label="kind")
    ignore_index = data.draw(st.booleans(), label="ignore_index")
    use_key = data.draw(st.booleans(), label="use_key")

    key = None
    if use_key:
        # A simple vectorized identity-preserving key (returns same shape Series).
        key = lambda s: s

    result = df.sort_values(
        by=by,
        axis=0,
        ascending=ascending,
        inplace=False,
        kind=kind,
        na_position=na_position,
        ignore_index=ignore_index,
        key=key,
    )

    # Property: shape preserved
    assert result.shape == df.shape

    # Property: columns unchanged
    assert list(result.columns) == list(df.columns)

    # Property: ignore_index relabeling
    if ignore_index:
        assert list(result.index) == list(range(len(df)))

    # Property: row-multiset preserved (sorting is a permutation of rows).
    # Compare as a sorted list of tuples using repr to handle NaN/mixed types.
    def rows_as_keyed_tuples(frame):
        out = []
        for _, row in frame.iterrows():
            out.append(tuple(repr(v) for v in row.tolist()))
        return sorted(out)

    assert rows_as_keyed_tuples(result) == rows_as_keyed_tuples(df)

    if len(result) >= 1:
        # Determine ascending direction for the primary (first) 'by' column.
        primary = by[0]
        if isinstance(ascending, list):
            primary_asc = ascending[0]
        else:
            primary_asc = ascending

        col = result[primary].tolist()

        def is_nan(v):
            return isinstance(v, float) and math.isnan(v)

        # Property: na_position placement for the primary column.
        nan_flags = [is_nan(v) for v in col]
        if any(nan_flags):
            if na_position == "last":
                # All NaNs must come after the last non-NaN.
                last_non_nan = max((i for i, f in enumerate(nan_flags) if not f),
                                   default=-1)
                first_nan = min(i for i, f in enumerate(nan_flags) if f)
                assert first_nan > last_non_nan or last_non_nan == -1
            else:  # 'first'
                last_nan = max(i for i, f in enumerate(nan_flags) if f)
                first_non_nan = min((i for i, f in enumerate(nan_flags) if not f),
                                    default=len(col))
                assert last_nan < first_non_nan or first_non_nan == len(col)

        # Property: non-NaN values of primary column are monotonic in the
        # requested direction (NaN entries are excluded from this check).
        non_nan_vals = [v for v in col if not is_nan(v)]
        for a, b in zip(non_nan_vals, non_nan_vals[1:]):
            if primary_asc:
                assert a <= b
            else:
                assert a >= b
# End program