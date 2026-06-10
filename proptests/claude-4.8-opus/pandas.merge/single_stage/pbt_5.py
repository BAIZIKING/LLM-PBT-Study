from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate two DataFrames sharing a key column drawn from a small
# pool (including None to test null-matching), with overlapping data columns,
# varying sizes including empty frames. Randomly choose how/sort/indicator/
# suffixes. Then verify return type, cross/inner/left/right/outer cardinality
# and key-coverage invariants, indicator column validity, and sort ordering.
@given(st.data())
def test_pandas_merge():
    data = st.data()

    # Pool of possible key values (including None for null-match edge case)
    key_pool = ['foo', 'bar', 'baz', 'qux', None]

    # Build the left DataFrame
    n_left = data.draw(st.integers(min_value=0, max_value=8), label="n_left")
    left_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=n_left, max_size=n_left),
        label="left_keys",
    )
    left = pd.DataFrame({
        'key': left_keys,
        'value': list(range(n_left)),          # overlapping column name
        'lonly': [f"L{i}" for i in range(n_left)],
    })

    # Build the right DataFrame
    n_right = data.draw(st.integers(min_value=0, max_value=8), label="n_right")
    right_keys = data.draw(
        st.lists(st.sampled_from(key_pool), min_size=n_right, max_size=n_right),
        label="right_keys",
    )
    right = pd.DataFrame({
        'key': right_keys,
        'value': list(range(100, 100 + n_right)),  # overlapping column name
        'ronly': [f"R{i}" for i in range(n_right)],
    })

    # Random parameters
    how = data.draw(
        st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']),
        label="how",
    )
    sort = data.draw(st.booleans(), label="sort")
    indicator = data.draw(st.booleans(), label="indicator")
    suffixes = data.draw(
        st.sampled_from([('_x', '_y'), ('_left', '_right'), ('_a', '_b')]),
        label="suffixes",
    )

    # Cross merge forbids 'on'; otherwise merge on the shared 'key' column.
    if how == 'cross':
        result = pd.merge(
            left, right, how='cross',
            sort=sort, suffixes=suffixes, indicator=indicator,
        )
    else:
        result = pd.merge(
            left, right, how=how, on='key',
            sort=sort, suffixes=suffixes, indicator=indicator,
        )

    # Property 1: result is always a DataFrame
    assert isinstance(result, pd.DataFrame)

    # Helper: set of non-null keys
    def key_set(keys):
        return {k for k in keys if k is not None}

    left_key_set = key_set(left_keys)
    right_key_set = key_set(right_keys)

    if how == 'cross':
        # Property 2: cross join is the full cartesian product
        assert len(result) == n_left * n_right

    else:
        result_keys = result['key'].tolist()
        result_key_set = key_set(result_keys)

        if how == 'inner':
            # Property 3: inner join keys are subset of both inputs' keys;
            # and bounded by cross product size.
            assert len(result) <= n_left * n_right
            for k in result_key_set:
                assert k in left_key_set and k in right_key_set

        elif how == 'left':
            # Property 4: every left key appears in the result
            assert left_key_set.issubset(result_key_set)

        elif how == 'right':
            # Property 5: every right key appears in the result
            assert right_key_set.issubset(result_key_set)

        elif how == 'outer':
            # Property 6: outer join keys == union of left and right keys
            assert result_key_set == (left_key_set | right_key_set)

    # Property 7: indicator column validity
    if indicator:
        assert '_merge' in result.columns
        valid = {'left_only', 'right_only', 'both'}
        assert set(result['_merge'].astype(str).unique()).issubset(valid)

    # Property 8: when sort=True (non-cross), non-null keys are sorted
    if sort and how != 'cross':
        non_null = [k for k in result['key'].tolist() if k is not None]
        assert non_null == sorted(non_null)
# End program