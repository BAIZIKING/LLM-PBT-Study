from hypothesis import given, strategies as st
import pandas


_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=5,
)
_VALUE = st.one_of(st.integers(min_value=-1000, max_value=1000), _TEXT)
_INDEX_VALUE = st.one_of(st.integers(min_value=-1000, max_value=1000), _TEXT)


def _draw_dataframe(data):
    n_rows = data.draw(st.integers(min_value=0, max_value=30), label="n_rows")
    n_cols = data.draw(st.integers(min_value=1, max_value=5), label="n_cols")

    columns = [f"c{i}" for i in range(n_cols)]
    frame_data = {
        col: data.draw(
            st.lists(_VALUE, min_size=n_rows, max_size=n_rows),
            label=f"values_{col}",
        )
        for col in columns
    }
    index = data.draw(
        st.lists(_INDEX_VALUE, min_size=n_rows, max_size=n_rows),
        label="index",
    )

    return pandas.DataFrame(frame_data, index=index), columns


def _draw_subset(data, columns):
    return data.draw(
        st.one_of(
            st.none(),
            st.sampled_from(columns),
            st.lists(st.sampled_from(columns), min_size=1, max_size=len(columns), unique=True),
        ),
        label="subset",
    )


def _subset_columns(df, subset):
    if subset is None:
        return list(df.columns)
    if isinstance(subset, list):
        return subset
    return [subset]


def _row_key(df, row_position, subset):
    cols = _subset_columns(df, subset)
    return tuple(df.iloc[row_position][col] for col in cols)


def _expected_positions(df, subset, keep):
    keys = [_row_key(df, i, subset) for i in range(len(df))]

    if keep == "first":
        seen = set()
        positions = []
        for i, key in enumerate(keys):
            if key not in seen:
                seen.add(key)
                positions.append(i)
        return positions

    if keep == "last":
        last_position = {}
        for i, key in enumerate(keys):
            last_position[key] = i
        return sorted(last_position.values())

    counts = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    return [i for i, key in enumerate(keys) if counts[key] == 1]


@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_no_duplicate_groups_remain(data):
    df, columns = _draw_dataframe(data)
    subset = _draw_subset(data, columns)
    keep = data.draw(st.sampled_from(["first", "last"]), label="keep")
    ignore_index = data.draw(st.booleans(), label="ignore_index")

    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)

    assert not bool(result.duplicated(subset=subset).any())


@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_keeps_requested_occurrence(data):
    df, columns = _draw_dataframe(data)
    subset = _draw_subset(data, columns)
    keep = data.draw(st.sampled_from(["first", "last"]), label="keep")

    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=False)
    expected = df.iloc[_expected_positions(df, subset, keep)]

    assert result.equals(expected)


@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_keep_false_removes_all_duplicate_groups(data):
    df, columns = _draw_dataframe(data)
    subset = _draw_subset(data, columns)

    result = df.drop_duplicates(subset=subset, keep=False, ignore_index=False)
    expected = df.iloc[_expected_positions(df, subset, False)]

    original_counts = {}
    for i in range(len(df)):
        key = _row_key(df, i, subset)
        original_counts[key] = original_counts.get(key, 0) + 1

    assert result.equals(expected)
    for i in range(len(result)):
        assert original_counts[_row_key(result, i, subset)] == 1


@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_retains_original_order_and_index_by_default(data):
    df, columns = _draw_dataframe(data)
    subset = _draw_subset(data, columns)
    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")

    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=False)
    expected_positions = _expected_positions(df, subset, keep)
    expected = df.iloc[expected_positions]

    assert result.equals(expected)
    assert list(result.index) == list(df.index.take(expected_positions))


@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property_ignore_index_relabels_result(data):
    df, columns = _draw_dataframe(data)
    subset = _draw_subset(data, columns)
    keep = data.draw(st.sampled_from(["first", "last", False]), label="keep")

    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=True)
    expected = df.iloc[_expected_positions(df, subset, keep)].reset_index(drop=True)

    assert result.equals(expected)
    assert list(result.index) == list(range(len(result)))


# End program