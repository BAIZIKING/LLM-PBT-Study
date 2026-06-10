from hypothesis import given, strategies as st
import pandas as pd
import numpy as np
import math

# Summary: Generate small-to-medium DataFrames with mixed dtypes (int, float-with-NaN,
# string) and named columns. Randomly choose a single column or subset of columns as
# `by`, with matching-length ascending bools, plus random na_position, ignore_index,
# and kind. Then verify shape/column preservation, that the result is a row permutation
# of the input, that the sort key is monotonic (single-key, NaN-free case), that NaNs are
# placed according to na_position, and that ignore_index relabels the axis correctly.
@given(st.data())
def test_pandas_DataFrame_sort_values(data):
    n_rows = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")
    n_cols = data.draw(st.integers(min_value=1, max_value=4), label="n_cols")

    col_names = [f"col{i}" for i in range(n_cols)]

    df_dict = {}
    for name in col_names:
        kind_of_col = data.draw(
            st.sampled_from(["int", "float", "str"]), label=f"dtype_{name}"
        )
        if kind_of_col == "int":
            values = data.draw(
                st.lists(
                    st.integers(min_value=-100, max_value=100),
                    min_size=n_rows, max_size=n_rows,
                ),
                label=f"vals_{name}",
            )
        elif kind_of_col == "float":
            values = data.draw(
                st.lists(
                    st.one_of(
                        st.floats(min_value=-100, max_value=100,
                                  allow_nan=False, allow_infinity=False),
                        st.just(float("nan")),
                    ),
                    min_size=n_rows, max_size=n_rows,
                ),
                label=f"vals_{name}",
            )
        else:  # str
            values = data.draw(
                st.lists(
                    st.text(alphabet="abcABC", min_size=0, max_size=3),
                    min_size=n_rows, max_size=n_rows,
                ),
                label=f"vals_{name}",
            )
        df_dict[name] = values

    df = pd.DataFrame(df_dict, columns=col_names)

    # Choose `by` as a single column or a non-empty subset of columns.
    use_list = data.draw(st.booleans(), label="by_is_list")
    if use_list:
        by = data.draw(
            st.lists(st.sampled_from(col_names), min_size=1, max_size=n_cols,
                     unique=True),
            label="by_list",
        )
        ascending = data.draw(
            st.lists(st.booleans(), min_size=len(by), max_size=len(by)),
            label="ascending_list",
        )
    else:
        by = data.draw(st.sampled_from(col_names), label="by_single")
        ascending = data.draw(st.booleans(), label="ascending_single")

    na_position = data.draw(st.sampled_from(["first", "last"]), label="na_position")
    ignore_index = data.draw(st.booleans(), label="ignore_index")
    kind = data.draw(
        st.sampled_from(["quicksort", "mergesort", "heapsort", "stable"]),
        label="kind",
    )

    result = df.sort_values(
        by=by,
        ascending=ascending,
        na_position=na_position,
        ignore_index=ignore_index,
        kind=kind,
    )

    # Property 1: shape and columns preserved.
    assert result.shape == df.shape
    assert list(result.columns) == list(df.columns)

    # Property 2: result is a row-permutation of the input (compare sorted row tuples).
    def row_multiset(frame):
        rows = []
        for _, row in frame.iterrows():
            rows.append(tuple(
                ("__nan__" if (isinstance(v, float) and math.isnan(v)) else v)
                for v in row.tolist()
            ))
        return sorted(rows, key=lambda t: tuple(str(x) for x in t))

    assert row_multiset(result) == row_multiset(df)

    # For single-key sorts, check monotonicity (NaN-free) and NaN placement.
    if not isinstance(by, list):
        col = result[by]
        is_float_col = col.dtype.kind == "f"
        if is_float_col:
            na_mask = col.isna().to_numpy()
            # Property 4: NaN positioning.
            if na_mask.any() and (~na_mask).any():
                idx = np.where(na_mask)[0]
                non_idx = np.where(~na_mask)[0]
                if na_position == "first":
                    assert idx.max() < non_idx.min()
                else:
                    assert idx.min() > non_idx.max()
            non_nan_vals = col[~col.isna()].tolist()
        else:
            non_nan_vals = col.tolist()

        # Property 3: monotonicity of the (NaN-free) sort key.
        for a, b in zip(non_nan_vals, non_nan_vals[1:]):
            if ascending:
                assert a <= b
            else:
                assert a >= b

    # Property 5 & 6: index handling.
    if ignore_index:
        assert list(result.index) == list(range(len(result)))
    else:
        assert sorted(result.index.tolist()) == sorted(df.index.tolist())
# End program