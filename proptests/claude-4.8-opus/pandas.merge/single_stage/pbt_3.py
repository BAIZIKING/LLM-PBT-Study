from hypothesis import given, strategies as st, settings
import pandas as pd
import numpy as np

# Summary: Generate two DataFrames sharing a key column ('key') plus possibly
# overlapping value columns, with varying row counts (including empty), duplicate
# and partially-overlapping key values, and random 'how'/'indicator'/'sort' flags.
# Then verify return type, indicator column validity, inner-join intersection
# semantics, left>=inner row count, cross-join cardinality, sort ordering, and
# preservation of non-overlapping columns.
@given(st.data())
@settings(deadline=None, max_examples=200)
def test_pandas_merge(data):
    # Pool of key values to encourage overlaps and non-overlaps
    key_pool = ['a', 'b', 'c', 'd', 'e']

    n_left = data.draw(st.integers(min_value=0, max_value=5), label="n_left")
    n_right = data.draw(st.integers(min_value=0, max_value=5), label="n_right")

    left_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=n_left, max_size=n_left),
        label="left_keys",
    )
    right_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=n_right, max_size=n_right),
        label="right_keys",
    )

    # Value columns: overlapping 'val' (tests suffixes) + unique cols
    left_val = data.draw(
        st.lists(st.integers(-100, 100), min_size=n_left, max_size=n_left),
        label="left_val",
    )
    right_val = data.draw(
        st.lists(st.integers(-100, 100), min_size=n_right, max_size=n_right),
        label="right_val",
    )

    df_left = pd.DataFrame({'key': left_keys, 'val': left_val, 'lonly': left_val})
    df_right = pd.DataFrame({'key': right_keys, 'val': right_val, 'ronly': right_val})

    how = data.draw(
        st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']), label="how"
    )
    indicator = data.draw(st.booleans(), label="indicator")
    sort = data.draw(st.booleans(), label="sort")

    if how == 'cross':
        result = pd.merge(
            df_left, df_right, how='cross', indicator=indicator, sort=sort
        )
    else:
        result = pd.merge(
            df_left, df_right, how=how, on='key', indicator=indicator, sort=sort
        )

    # Property 1: return type is DataFrame
    assert isinstance(result, pd.DataFrame)

    # Property 2: indicator column validity
    if indicator:
        assert '_merge' in result.columns
        assert isinstance(result['_merge'].dtype, pd.CategoricalDtype)
        valid = {'left_only', 'right_only', 'both'}
        assert set(result['_merge'].astype(str).unique()).issubset(valid)

    if how == 'cross':
        # Property 5: cross join cardinality
        assert len(result) == len(df_left) * len(df_right)
        # Cross merge keeps both key columns (suffixed)
        assert {'key_x', 'key_y'}.issubset(result.columns)
    else:
        # Property 7: non-overlapping columns preserved; key present once
        assert 'key' in result.columns
        assert 'lonly' in result.columns
        assert 'ronly' in result.columns

        left_key_set = set(df_left['key'].unique())
        right_key_set = set(df_right['key'].unique())
        result_keys = set(result['key'].dropna().unique())

        if how == 'inner':
            # Property 3: inner join keys are subset of intersection
            assert result_keys.issubset(left_key_set & right_key_set)

        # Compute inner-join row count for comparison
        inner = pd.merge(df_left, df_right, how='inner', on='key')

        if how == 'left':
            # Property 4: left join has >= inner-join rows
            assert len(result) >= len(inner)
            # Every left key present in result
            assert left_key_set.issubset(result_keys | {None})

        if how == 'right':
            assert len(result) >= len(inner)

        # Property 6: sort=True yields lexicographically sorted keys
        if sort and len(result) > 1:
            keys = list(result['key'].dropna())
            assert keys == sorted(keys)
# End program