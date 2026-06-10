from hypothesis import given, strategies as st, settings, assume
import pandas as pd
import numpy as np
import math


# Strategy for generating a DataFrame with sortable columns and an arbitrary index.
@st.composite
def dataframes(draw, min_rows=0, max_rows=20, min_cols=1, max_cols=4):
    n_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    n_cols = draw(st.integers(min_value=min_cols, max_value=max_cols))

    # Each column is either integers, floats (possibly with NaN), or strings.
    col_kinds = draw(
        st.lists(
            st.sampled_from(["int", "float", "str"]),
            min_size=n_cols,
            max_size=n_cols,
        )
    )

    data = {}
    for i, kind in enumerate(col_kinds):
        col_name = f"col{i}"
        if kind == "int":
            values = draw(
                st.lists(
                    st.integers(min_value=-10_000, max_value=10_000),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )
        elif kind == "float":
            values = draw(
                st.lists(
                    st.one_of(
                        st.floats(
                            min_value=-1e9,
                            max_value=1e9,
                            allow_nan=True,
                            allow_infinity=False,
                        ),
                    ),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )
        else:  # str
            values = draw(
                st.lists(
                    st.text(
                        alphabet="abcdefghijABCDEFGHIJ",
                        min_size=0,
                        max_size=5,
                    ),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )
        data[col_name] = values

    # Generate a (possibly non-default) unique index.
    index_values = draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=n_rows,
            max_size=n_rows,
            unique=True,
        )
    )

    df = pd.DataFrame(data, index=index_values)
    return df


def _multiset_of_rows(df):
    """Return a sorted list of row tuples for multiset comparison (NaN-aware)."""
    rows = []
    for _, row in df.iterrows():
        tup = tuple(
            ("__nan__" if (isinstance(v, float) and math.isnan(v)) else v)
            for v in row.values
        )
        rows.append(tup)
    # Sort by string representation for a stable, comparison-safe ordering.
    return sorted(rows, key=lambda t: repr(t))


# Property 1: Same shape and same multiset of rows.
@settings(max_examples=200)
@given(st.data())
def test_pandas_DataFrame_sort_values_preserves_rows():
    data = st.data()

@settings(max_examples=200)
@given(df=dataframes(), data=st.data())
def test_preserves_shape_and_rows(df, data):
    by = data.draw(st.sampled_from(list(df.columns)))
    result = df.sort_values(by=by)
    assert result.shape == df.shape
    assert _multiset_of_rows(result) == _multiset_of_rows(df)


# Property 2: Single column sort yields ordered non-NaN values.
@settings(max_examples=200)
@given(df=dataframes(), data=st.data())
def test_single_column_ordering(df, data):
    assume(len(df) > 0)
    by = data.draw(st.sampled_from(list(df.columns)))
    ascending = data.draw(st.booleans())
    result = df.sort_values(by=by, ascending=ascending)

    col = result[by]
    # Drop NaNs and check ordering on the remaining values.
    non_na = [v for v in col.tolist() if not (isinstance(v, float) and math.isnan(v))]
    if ascending:
        assert all(non_na[i] <= non_na[i + 1] for i in range(len(non_na) - 1))
    else:
        assert all(non_na[i] >= non_na[i + 1] for i in range(len(non_na) - 1))


# Property 3: NaN positioning according to na_position.
@settings(max_examples=200)
@given(df=dataframes(), data=st.data())
def test_na_position(df, data):
    assume(len(df) > 0)
    by = data.draw(st.sampled_from(list(df.columns)))
    ascending = data.draw(st.booleans())
    na_position = data.draw(st.sampled_from(["first", "last"]))
    result = df.sort_values(by=by, ascending=ascending, na_position=na_position)

    col = result[by].tolist()
    is_nan = [isinstance(v, float) and math.isnan(v) for v in col]
    n_nan = sum(is_nan)
    assume(n_nan > 0)

    if na_position == "first":
        # All NaNs must be at the beginning.
        assert all(is_nan[:n_nan])
    else:
        # All NaNs must be at the end.
        assert all(is_nan[len(is_nan) - n_nan:])


# Property 4: ignore_index controls the resulting index.
@settings(max_examples=200)
@given(df=dataframes(), data=st.data())
def test_ignore_index(df, data):
    by = data.draw(st.sampled_from(list(df.columns)))

    result_ignore = df.sort_values(by=by, ignore_index=True)
    assert list(result_ignore.index) == list(range(len(df)))

    result_keep = df.sort_values(by=by, ignore_index=False)
    # Original index labels must be preserved (as a multiset).
    assert sorted(result_keep.index.tolist()) == sorted(df.index.tolist())


# Property 5: inplace behavior.
@settings(max_examples=200)
@given(df=dataframes(), data=st.data())
def test_inplace_behavior(df, data):
    by = data.draw(st.sampled_from(list(df.columns)))

    # Non-inplace: original unchanged, returns new sorted frame.
    df_copy = df.copy(deep=True)
    returned = df.sort_values(by=by, inplace=False)
    assert returned is not None
    # Original df unchanged.
    pd.testing.assert_frame_equal(df, df_copy)

    # Inplace: returns None, df modified to match non-inplace result.
    df_inplace = df.copy(deep=True)
    ret = df_inplace.sort_values(by=by, inplace=True)
    assert ret is None
    pd.testing.assert_frame_equal(df_inplace, returned)
# End program