from hypothesis import given, strategies as st, settings
import pandas as pd
import numpy as np
import math

# Summary: Generate DataFrames with mixed int/float(with NaN)/string columns of
# random length, then randomly pick `by` columns, ascending (bool or list of
# bools matching `by`), na_position, ignore_index, and kind. Check that sorting
# preserves shape/columns/multiset of values, that single-column ascending sorts
# are correctly ordered, that na_position places NaNs correctly, and that
# ignore_index relabels the index as 0..n-1.
@given(st.data())
@settings(max_examples=200)
def test_pandas_DataFrame_sort_values(data):
    n = data.draw(st.integers(min_value=0, max_value=8), label="n_rows")

    int_col = data.draw(
        st.lists(st.integers(min_value=-50, max_value=50), min_size=n, max_size=n),
        label="int_col",
    )
    float_col = data.draw(
        st.lists(
            st.one_of(
                st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
                st.just(float("nan")),
            ),
            min_size=n, max_size=n,
        ),
        label="float_col",
    )
    str_col = data.draw(
        st.lists(st.text(alphabet="abcABC", min_size=0, max_size=3), min_size=n, max_size=n),
        label="str_col",
    )

    df = pd.DataFrame({"i": int_col, "f": float_col, "s": str_col})

    columns = ["i", "f", "s"]
    by = data.draw(
        st.lists(st.sampled_from(columns), min_size=1, max_size=3, unique=True),
        label="by",
    )

    # ascending: either a single bool, or a list of bools matching len(by)
    use_list = data.draw(st.booleans(), label="asc_is_list")
    if use_list:
        ascending = data.draw(
            st.lists(st.booleans(), min_size=len(by), max_size=len(by)),
            label="ascending_list",
        )
    else:
        ascending = data.draw(st.booleans(), label="ascending_scalar")

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

    # Property 1: shape preserved
    assert result.shape == df.shape

    # Property 2: columns preserved
    assert list(result.columns) == list(df.columns)

    # Property 3: multiset of values preserved per column (permutation of rows)
    for c in df.columns:
        orig = df[c].tolist()
        res = result[c].tolist()
        # Compare as multisets, treating NaN by representation to avoid NaN != NaN
        def norm(v):
            if isinstance(v, float) and math.isnan(v):
                return ("__nan__",)
            return (v,)
        assert sorted(map(norm, orig)) == sorted(map(norm, res))

    # Property 4: index behavior
    if ignore_index:
        assert list(result.index) == list(range(len(result)))
    else:
        assert sorted(result.index.tolist()) == sorted(df.index.tolist())

    # Property 5: single-column ascending sort is correctly ordered (ignoring NaNs)
    asc_scalar = ascending if isinstance(ascending, bool) else None
    if len(by) == 1 and asc_scalar is True:
        col = by[0]
        vals = result[col].tolist()
        # separate NaNs from non-NaNs
        non_nan = [v for v in vals if not (isinstance(v, float) and math.isnan(v))]
        # non-NaN portion must be sorted ascending
        assert non_nan == sorted(non_nan)

    # Property 6: NaN placement for the (single) float sort column
    if len(by) == 1 and by[0] == "f":
        vals = result["f"].tolist()
        nan_flags = [isinstance(v, float) and math.isnan(v) for v in vals]
        num_nan = sum(nan_flags)
        if num_nan > 0:
            if na_position == "last":
                assert nan_flags[-num_nan:] == [True] * num_nan
                assert not any(nan_flags[:-num_nan])
            else:  # "first"
                assert nan_flags[:num_nan] == [True] * num_nan
                assert not any(nan_flags[num_nan:])
# End program