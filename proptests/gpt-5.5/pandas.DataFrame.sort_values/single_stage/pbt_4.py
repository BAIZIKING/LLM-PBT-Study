from hypothesis import given, strategies as st
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from collections import Counter

# Summary: Generate small numeric DataFrames with duplicates, ties, NaNs, infinities, varied row/column counts, both sort axes, scalar/list `by`, scalar/list `ascending`, all documented `kind`/`na_position` values, both `ignore_index`/`inplace` modes, and optional vectorized key functions. Check that valid calls sort adjacent records according to the transformed keys, preserve shape and data as a permutation along the sorted axis, honor inplace return behavior, and relabel the sorted axis when `ignore_index=True`.
@given(st.data())
def test_pandas_DataFrame_sort_values(data):
    n_rows = data.draw(st.integers(min_value=1, max_value=8))
    n_cols = data.draw(st.integers(min_value=1, max_value=6))

    cell = st.one_of(
        st.integers(min_value=-5, max_value=5),
        st.floats(allow_nan=False, allow_infinity=True, width=32),
        st.just(np.nan),
    )
    matrix = data.draw(
        st.lists(
            st.lists(cell, min_size=n_cols, max_size=n_cols),
            min_size=n_rows,
            max_size=n_rows,
        )
    )

    columns = [f"c{i}" for i in range(n_cols)]
    index = [f"r{i}" for i in range(n_rows)]
    df = pd.DataFrame(matrix, columns=columns, index=index)
    original = df.copy(deep=True)

    axis = data.draw(st.sampled_from([0, "index", 1, "columns"]))
    effective_axis = 0 if axis in (0, "index") else 1

    by_pool = columns if effective_axis == 0 else index
    by_len = data.draw(st.integers(min_value=1, max_value=min(3, len(by_pool))))
    by_list = data.draw(
        st.lists(st.sampled_from(by_pool), min_size=by_len, max_size=by_len, unique=True)
    )
    by = by_list[0] if by_len == 1 and data.draw(st.booleans()) else by_list

    if data.draw(st.booleans()):
        ascending = data.draw(st.booleans())
        ascending_list = [ascending] * by_len
    else:
        ascending_list = data.draw(
            st.lists(st.booleans(), min_size=by_len, max_size=by_len)
        )
        ascending = ascending_list

    inplace = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(["quicksort", "mergesort", "heapsort", "stable"]))
    na_position = data.draw(st.sampled_from(["first", "last"]))
    ignore_index = data.draw(st.booleans())

    key_name = data.draw(st.sampled_from(["none", "identity", "negate", "absolute"]))
    if key_name == "none":
        key = None
    elif key_name == "identity":
        key = lambda s: s
    elif key_name == "negate":
        key = lambda s: -s
    else:
        key = lambda s: s.abs()

    returned = df.sort_values(
        by=by,
        axis=axis,
        ascending=ascending,
        inplace=inplace,
        kind=kind,
        na_position=na_position,
        ignore_index=ignore_index,
        key=key,
    )

    if inplace:
        assert returned is None
        result = df
    else:
        result = returned
        assert isinstance(result, pd.DataFrame)
        assert_frame_equal(df, original)

    assert result.shape == original.shape

    if effective_axis == 0:
        assert list(result.columns) == list(original.columns)
        if ignore_index:
            assert list(result.index) == list(range(n_rows))
        else:
            assert Counter(result.index) == Counter(original.index)
    else:
        assert list(result.index) == list(original.index)
        if ignore_index:
            assert list(result.columns) == list(range(n_cols))
        else:
            assert Counter(result.columns) == Counter(original.columns)

    def normalize(value):
        return "<NA>" if pd.isna(value) else value

    if effective_axis == 0:
        original_rows = Counter(
            tuple(normalize(v) for v in original.iloc[i, :].tolist())
            for i in range(n_rows)
        )
        result_rows = Counter(
            tuple(normalize(v) for v in result.iloc[i, :].tolist())
            for i in range(n_rows)
        )
        assert result_rows == original_rows
    else:
        original_cols = Counter(
            tuple(normalize(v) for v in original.iloc[:, j].tolist())
            for j in range(n_cols)
        )
        result_cols = Counter(
            tuple(normalize(v) for v in result.iloc[:, j].tolist())
            for j in range(n_cols)
        )
        assert result_cols == original_cols

    key_arrays = []
    if effective_axis == 0:
        for label in by_list:
            series = result[label]
            transformed = key(series) if key is not None else series
            key_arrays.append(list(transformed.to_numpy()))
        sorted_length = n_rows
    else:
        for label in by_list:
            series = result.loc[label, :]
            transformed = key(series) if key is not None else series
            key_arrays.append(list(transformed.to_numpy()))
        sorted_length = n_cols

    def adjacent_pair_is_ordered(left_pos, right_pos):
        for values, asc in zip(key_arrays, ascending_list):
            left = values[left_pos]
            right = values[right_pos]
            left_is_na = bool(pd.isna(left))
            right_is_na = bool(pd.isna(right))

            if left_is_na and right_is_na:
                continue
            if left_is_na or right_is_na:
                return left_is_na if na_position == "first" else right_is_na
            if left == right:
                continue
            return left < right if asc else left > right
        return True

    for pos in range(sorted_length - 1):
        assert adjacent_pair_is_ordered(pos, pos + 1)

# End program