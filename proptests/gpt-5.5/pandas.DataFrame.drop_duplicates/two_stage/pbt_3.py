from hypothesis import given, strategies as st
import pandas

@given(st.data())
def test_pandas_DataFrame_drop_duplicates_property(data):
    cell_values = st.one_of(
        st.none(),
        st.integers(min_value=-1000, max_value=1000),
        st.text(min_size=0, max_size=5),
    )

    rows = data.draw(
        st.lists(
            st.tuples(cell_values, cell_values, cell_values),
            min_size=0,
            max_size=30,
        )
    )

    index_values = st.one_of(
        st.none(),
        st.integers(min_value=-1000, max_value=1000),
        st.text(min_size=0, max_size=5),
    )
    index = data.draw(
        st.lists(index_values, min_size=len(rows), max_size=len(rows))
    )

    subset = data.draw(
        st.sampled_from(
            [
                None,
                "a",
                "b",
                "c",
                ["a"],
                ["b"],
                ["c"],
                ["a", "b"],
                ["a", "c"],
                ["b", "c"],
                ["a", "b", "c"],
            ]
        )
    )
    keep = data.draw(st.sampled_from(["first", "last", False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())

    original = pandas.DataFrame(rows, columns=["a", "b", "c"])
    original.index = pandas.Index(index)

    if subset is None:
        subset_columns = ["a", "b", "c"]
    elif isinstance(subset, str):
        subset_columns = [subset]
    else:
        subset_columns = list(subset)

    def key_at(frame, position):
        return tuple(frame.iloc[position][column] for column in subset_columns)

    keys = []
    counts = {}
    for position in range(len(original)):
        key = key_at(original, position)
        keys.append(key)
        counts[key] = counts.get(key, 0) + 1

    if keep == "first":
        seen = set()
        expected_positions = []
        for position, key in enumerate(keys):
            if key not in seen:
                seen.add(key)
                expected_positions.append(position)
    elif keep == "last":
        last_position = {}
        for position, key in enumerate(keys):
            last_position[key] = position
        expected_positions = [
            position
            for position, key in enumerate(keys)
            if last_position[key] == position
        ]
    else:
        expected_positions = [
            position
            for position, key in enumerate(keys)
            if counts[key] == 1
        ]

    df = original.copy(deep=True)
    result = df.drop_duplicates(
        subset=subset,
        keep=keep,
        inplace=inplace,
        ignore_index=ignore_index,
    )

    if inplace:
        assert result is None
        output = df
    else:
        output = result
        pandas.testing.assert_frame_equal(df, original)

    expected = original.iloc[expected_positions].copy()
    if ignore_index:
        expected = expected.reset_index(drop=True)

    pandas.testing.assert_frame_equal(output, expected)

    assert list(output.columns) == list(original.columns)

    if ignore_index:
        assert list(output.index) == list(range(len(output)))
    else:
        assert list(output.index) == list(original.iloc[expected_positions].index)

    assert expected_positions == sorted(expected_positions)

    seen_output_keys = set()
    for position in range(len(output)):
        key = key_at(output, position)
        assert key not in seen_output_keys
        seen_output_keys.add(key)

        if keep is False:
            assert counts[key] == 1

# End program