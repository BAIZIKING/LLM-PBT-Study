from hypothesis import given, strategies as st
import pandas as pd
from pandas.testing import assert_frame_equal

# Summary: Generate duplicate-prone DataFrames with random row counts, column labels,
# scalar values including null-like/NaN/infinite values, and varied indexes including
# integer, string, and DatetimeIndex values. Randomly generate all drop_duplicates
# parameters: subset=None/scalar/list, keep='first'/'last'/False, inplace bool, and
# ignore_index bool. Check that duplicates are removed according to duplicated(),
# that keep semantics match the documented mask, that inplace controls the return
# value and mutation behavior, that ignore_index resets the index, and that row
# indexes are ignored when identifying duplicates.
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    n_rows = data.draw(st.integers(min_value=0, max_value=30), label="n_rows")
    n_cols = data.draw(st.integers(min_value=1, max_value=5), label="n_cols")

    column_label = st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=1,
        max_size=4,
    )
    columns = data.draw(
        st.lists(column_label, min_size=n_cols, max_size=n_cols, unique=True),
        label="columns",
    )

    cell = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-3, max_value=3),
        st.sampled_from(["", "x", "y"]),
        st.sampled_from([float("nan"), float("inf"), float("-inf"), -0.0, 0.0, 1.5]),
    )

    if n_rows == 0:
        rows = []
    else:
        # Build rows from a small template pool so exact duplicate rows and
        # duplicate subsets are common, while still allowing mixed edge values.
        pool_size = data.draw(
            st.integers(min_value=1, max_value=min(6, n_rows)),
            label="pool_size",
        )
        row_template = st.lists(cell, min_size=n_cols, max_size=n_cols)
        templates = data.draw(
            st.lists(row_template, min_size=pool_size, max_size=pool_size),
            label="row_templates",
        )
        row_choices = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=pool_size - 1),
                min_size=n_rows,
                max_size=n_rows,
            ),
            label="row_choices",
        )
        rows = [list(templates[i]) for i in row_choices]

    df = pd.DataFrame(rows, columns=columns)

    index_kind = data.draw(
        st.sampled_from(["range", "int", "str", "datetime"]),
        label="index_kind",
    )
    if index_kind == "int":
        df.index = pd.Index(
            data.draw(
                st.lists(
                    st.integers(min_value=-5, max_value=5),
                    min_size=n_rows,
                    max_size=n_rows,
                ),
                label="int_index",
            )
        )
    elif index_kind == "str":
        df.index = pd.Index(
            data.draw(
                st.lists(
                    st.text(
                        alphabet=st.characters(blacklist_categories=("Cs",)),
                        min_size=0,
                        max_size=3,
                    ),
                    min_size=n_rows,
                    max_size=n_rows,
                ),
                label="str_index",
            )
        )
    elif index_kind == "datetime":
        offsets = data.draw(
            st.lists(
                st.integers(min_value=-5, max_value=5),
                min_size=n_rows,
                max_size=n_rows,
            ),
            label="datetime_offsets",
        )
        df.index = pd.Timestamp("2020-01-01") + pd.to_timedelta(offsets, unit="D")

    subset_kind = data.draw(
        st.sampled_from(["none", "scalar", "list"]),
        label="subset_kind",
    )
    if subset_kind == "none":
        subset = None
    elif subset_kind == "scalar":
        subset = data.draw(st.sampled_from(columns), label="subset_scalar")
    else:
        subset = data.draw(
            st.lists(
                st.sampled_from(columns),
                min_size=1,
                max_size=n_cols,
                unique=True,
            ),
            label="subset_list",
        )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    inplace = data.draw(st.booleans(), label="inplace")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    before = df.copy(deep=True)

    returned = df.drop_duplicates(
        subset=subset,
        keep=keep,
        inplace=inplace,
        ignore_index=ignore_index,
    )

    expected_mask = ~before.duplicated(subset=subset, keep=keep)
    expected = before.iloc[expected_mask.to_numpy()]
    if ignore_index:
        expected = expected.reset_index(drop=True)

    if inplace:
        assert returned is None
        result = df
    else:
        assert isinstance(returned, pd.DataFrame)
        result = returned
        assert_frame_equal(df, before)

    assert_frame_equal(result, expected)

    # The result should contain no remaining duplicate rows for the selected subset.
    assert not bool(result.duplicated(subset=subset, keep=False).any())

    # ignore_index=True must label the resulting axis 0, 1, ..., n - 1.
    if ignore_index:
        assert list(result.index) == list(range(len(result)))

    # Index values must not affect which rows are considered duplicates.
    reindexed = before.copy(deep=True)
    reindexed.index = pd.RangeIndex(start=10_000, stop=10_000 + len(reindexed))
    assert_frame_equal(
        before.drop_duplicates(subset=subset, keep=keep, ignore_index=True),
        reindexed.drop_duplicates(subset=subset, keep=keep, ignore_index=True),
    )
# End program