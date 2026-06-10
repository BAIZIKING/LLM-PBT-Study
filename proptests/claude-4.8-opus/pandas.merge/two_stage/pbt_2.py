from hypothesis import given, strategies as st, settings, HealthCheck
import pandas as pd
import pandas.testing as pdt


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Safe scalar values for cell contents (avoid NaN-in-keys edge cases, overflows)
def safe_keys():
    return st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.sampled_from(['foo', 'bar', 'baz', 'qux', 'a', 'b', 'c']),
    )


def safe_values():
    return st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.sampled_from(['x', 'y', 'z']),
    )


@st.composite
def two_dataframes(draw, max_rows=8):
    """Generate two DataFrames that share a common key column 'key'
    plus possibly overlapping and distinct value columns."""
    n_left = draw(st.integers(min_value=0, max_value=max_rows))
    n_right = draw(st.integers(min_value=0, max_value=max_rows))

    left_keys = draw(st.lists(safe_keys(), min_size=n_left, max_size=n_left))
    right_keys = draw(st.lists(safe_keys(), min_size=n_right, max_size=n_right))

    left_vals = draw(st.lists(safe_values(), min_size=n_left, max_size=n_left))
    right_vals = draw(st.lists(safe_values(), min_size=n_right, max_size=n_right))

    # ensure all left_keys are valid python objects; key dtype consistent
    left = pd.DataFrame({'key': left_keys, 'lval': left_vals})
    right = pd.DataFrame({'key': right_keys, 'rval': right_vals})

    # cast key columns to object so int/str mixing doesn't break dtype matching
    left['key'] = left['key'].astype(object)
    right['key'] = right['key'].astype(object)

    return left, right


# ---------------------------------------------------------------------------
# Property 1: Cross-join row count and columns
# ---------------------------------------------------------------------------
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.data())
def test_pandas_merge_cross_rowcount():
    @given(two_dataframes())
    def inner(dfs):
        left, right = dfs
        result = pd.merge(left, right, how='cross')
        # row count is the product
        assert len(result) == len(left) * len(right)
        # columns are union of left and right columns (no overlap here:
        # 'key' appears in both, so suffixes applied)
        expected_cols = {'key_x', 'lval', 'key_y', 'rval'}
        assert set(result.columns) == expected_cols
    inner()
# End program


# ---------------------------------------------------------------------------
# Property 2: Inner join is a subset of outer join (and row count ordering)
# ---------------------------------------------------------------------------
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.data())
def test_pandas_merge_inner_subset_of_outer():
    @given(two_dataframes())
    def inner(dfs):
        left, right = dfs
        inner_res = pd.merge(left, right, how='inner', on='key')
        outer_res = pd.merge(left, right, how='outer', on='key')
        left_res = pd.merge(left, right, how='left', on='key')
        right_res = pd.merge(left, right, how='right', on='key')

        # row count ordering
        assert len(inner_res) <= len(outer_res)
        assert len(inner_res) <= len(left_res)
        assert len(inner_res) <= len(right_res)

        # inner rows are a subset of outer rows (as multisets of tuples)
        def row_multiset(df):
            from collections import Counter
            return Counter(tuple(r) for r in df.itertuples(index=False, name=None))

        inner_ms = row_multiset(inner_res)
        outer_ms = row_multiset(outer_res)
        for row, count in inner_ms.items():
            assert outer_ms.get(row, 0) >= count
    inner()
# End program


# ---------------------------------------------------------------------------
# Property 3: Indicator value correctness
# ---------------------------------------------------------------------------
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.data())
def test_pandas_merge_indicator():
    @given(two_dataframes(), st.sampled_from(['inner', 'left', 'right', 'outer']))
    def inner(dfs, how):
        left, right = dfs
        result = pd.merge(left, right, how=how, on='key', indicator=True)
        allowed = {'left_only', 'right_only', 'both'}
        vals = set(result['_merge'].astype(str).unique())
        assert vals.issubset(allowed)

        if how == 'inner':
            assert vals.issubset({'both'})
        elif how == 'left':
            assert 'right_only' not in vals
        elif how == 'right':
            assert 'left_only' not in vals
    inner()
# End program


# ---------------------------------------------------------------------------
# Property 4: Output column structure (suffixes applied to overlap)
# ---------------------------------------------------------------------------
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.data())
def test_pandas_merge_column_structure():
    @given(two_dataframes(), st.sampled_from(['inner', 'left', 'right', 'outer']))
    def inner(dfs, how):
        left, right = dfs
        result = pd.merge(left, right, how=how, on='key')
        # key is a join column -> single 'key' column
        # 'lval' and 'rval' are distinct -> kept as-is
        expected_cols = {'key', 'lval', 'rval'}
        assert set(result.columns) == expected_cols
        # number of columns: left cols + right cols - shared join keys
        assert len(result.columns) == 3
    inner()
# End program


# ---------------------------------------------------------------------------
# Property 5: Left join preserves all left keys; right join preserves right keys
# ---------------------------------------------------------------------------
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.data())
def test_pandas_merge_left_right_preserve_keys():
    @given(two_dataframes())
    def inner(dfs):
        left, right = dfs

        left_res = pd.merge(left, right, how='left', on='key')
        # every left key appears in the output
        assert set(left['key']) == set(left_res['key'])
        # row count at least len(left)
        assert len(left_res) >= len(left)

        right_res = pd.merge(left, right, how='right', on='key')
        assert set(right['key']) == set(right_res['key'])
        assert len(right_res) >= len(right)
    inner()
# End program