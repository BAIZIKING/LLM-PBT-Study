from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate DataFrames with 0-5 uniquely named columns, 0-20 rows, mixed scalar
# values including None, booleans, small integers, finite/special floats, and strings.
# Rows are sampled from a smaller pool to intentionally create duplicates. Generate varied
# indexes, including duplicated object indexes and DatetimeIndex values, because the API
# says indexes are ignored. Generate all drop_duplicates parameters: subset=None, a single
# column label, or a non-empty sequence of labels; keep='first', keep='last', or False;
# inplace=True/False; and ignore_index=True/False.
@given(st.data())
def test_pandas_DataFrame_drop_duplicates(data):
    text_alphabet = list("abcXYZ012_")
    text_values = st.text(alphabet=st.sampled_from(text_alphabet), min_size=0, max_size=4)
    column_labels = st.text(alphabet=st.sampled_from(text_alphabet), min_size=1, max_size=4)

    scalar_values = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-3, max_value=3),
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False, width=32),
        st.sampled_from([float("nan"), float("inf"), -float("inf")]),
        text_values,
    )

    n_cols = data.draw(st.integers(min_value=0, max_value=5), label="n_cols")
    columns = data.draw(
        st.lists(column_labels, min_size=n_cols, max_size=n_cols, unique=True),
        label="columns",
    )

    n_rows = data.draw(st.integers(min_value=0, max_value=20), label="n_rows")

    if n_cols == 0:
        row_strategy = st.just(())
    else:
        row_strategy = st.tuples(*[scalar_values for _ in range(n_cols)])

    if n_rows == 0:
        rows = []
    else:
        pool_size = data.draw(
            st.integers(min_value=1, max_value=min(n_rows, 8)),
            label="duplicate_row_pool_size",
        )
        row_pool = data.draw(
            st.lists(row_strategy, min_size=pool_size, max_size=pool_size),
            label="duplicate_row_pool",
        )
        rows = data.draw(
            st.lists(st.sampled_from(row_pool), min_size=n_rows, max_size=n_rows),
            label="rows",
        )

    df = pd.DataFrame(rows, columns=columns)

    index_kind = data.draw(st.sampled_from(["range", "object", "datetime"]), label="index_kind")
    if index_kind == "object":
        index_values = data.draw(
            st.lists(
                st.one_of(st.none(), st.integers(min_value=-5, max_value=5), text_values),
                min_size=n_rows,
                max_size=n_rows,
            ),
            label="object_index_values",
        )
        df.index = pd.Index(index_values)
    elif index_kind == "datetime":
        offsets = data.draw(
            st.lists(st.integers(min_value=-5, max_value=5), min_size=n_rows, max_size=n_rows),
            label="datetime_index_offsets",
        )
        df.index = pd.DatetimeIndex(
            [pd.Timestamp("2020-01-01") + pd.Timedelta(days=o) for o in offsets]
        )

    if n_cols == 0:
        subset = None
    else:
        subset_sequence = st.lists(
            st.sampled_from(columns),
            min_size=1,
            max_size=n_cols,
            unique=True,
        )
        subset = data.draw(
            st.one_of(
                st.none(),
                st.sampled_from(columns),
                subset_sequence,
                subset_sequence.map(tuple),
            ),
            label="subset",
        )

    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")
    inplace = data.draw(st.booleans(), label="inplace")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    original = df.copy(deep=True)
    working = df.copy(deep=True)
    before_call = working.copy(deep=True)

    # Property 1: drop_duplicates should keep exactly the rows that are not marked
    # duplicated according to subset and keep, preserving row order.
    keep_mask = (~original.duplicated(subset=subset, keep=keep)).to_numpy()
    expected = original.iloc[keep_mask].copy()
    if ignore_index:
        expected = expected.reset_index(drop=True)

    result = working.drop_duplicates(
        subset=subset,
        keep=keep,
        inplace=inplace,
        ignore_index=ignore_index,
    )

    # Property 2: return value follows inplace semantics.
    if inplace:
        assert result is None
        observed = working
    else:
        assert isinstance(result, pd.DataFrame)
        observed = result

        # Property 3: when inplace=False, the input DataFrame is not modified.
        pd.testing.assert_frame_equal(working, before_call)

    pd.testing.assert_frame_equal(observed, expected)

    # Property 4: the result has no remaining duplicate rows under the selected subset.
    assert not observed.duplicated(subset=subset, keep=False).any()

    # Property 5: indexes are ignored when identifying duplicates. With ignore_index=True,
    # two DataFrames with identical column data but different indexes should produce the
    # same duplicate-removal result.
    different_index = original.copy(deep=True)
    different_index.index = pd.Index(range(10_000, 10_000 + n_rows))

    original_index_ignored = original.drop_duplicates(
        subset=subset,
        keep=keep,
        ignore_index=True,
    )
    different_index_ignored = different_index.drop_duplicates(
        subset=subset,
        keep=keep,
        ignore_index=True,
    )

    pd.testing.assert_frame_equal(original_index_ignored, different_index_ignored)

# End program