from hypothesis import given, strategies as st
import pandas

@given(st.data())
def test_pandas_DataFrame_sort_values_property_lexicographic_order(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    a = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    b = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    payload = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    ascending = data.draw(st.lists(st.booleans(), min_size=2, max_size=2))

    df = pandas.DataFrame({"a": a, "b": b, "payload": payload})
    result = df.sort_values(by=["a", "b"], ascending=ascending)

    sort_keys = [
        (
            x if ascending[0] else -x,
            y if ascending[1] else -y,
        )
        for x, y in zip(result["a"].tolist(), result["b"].tolist())
    ]

    assert all(sort_keys[i] <= sort_keys[i + 1] for i in range(len(sort_keys) - 1))


@given(st.data())
def test_pandas_DataFrame_sort_values_property_na_position(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    values = data.draw(
        st.lists(
            st.one_of(
                st.none(),
                st.floats(
                    min_value=-1_000_000,
                    max_value=1_000_000,
                    allow_nan=False,
                    allow_infinity=False,
                    width=32,
                ),
            ),
            min_size=n,
            max_size=n,
        )
    )
    ascending = data.draw(st.booleans())
    na_position = data.draw(st.sampled_from(["first", "last"]))

    df = pandas.DataFrame({"x": values, "payload": list(range(n))})
    result = df.sort_values(by="x", ascending=ascending, na_position=na_position)

    sorted_values = result["x"].tolist()
    missing_mask = [pandas.isna(x) for x in sorted_values]
    missing_count = sum(missing_mask)

    if na_position == "first":
        assert missing_mask[:missing_count] == [True] * missing_count
        assert missing_mask[missing_count:] == [False] * (len(missing_mask) - missing_count)
    else:
        assert missing_mask[: len(missing_mask) - missing_count] == [False] * (
            len(missing_mask) - missing_count
        )
        assert missing_mask[len(missing_mask) - missing_count :] == [True] * missing_count

    non_missing = [x for x in sorted_values if not pandas.isna(x)]
    if ascending:
        assert all(non_missing[i] <= non_missing[i + 1] for i in range(len(non_missing) - 1))
    else:
        assert all(non_missing[i] >= non_missing[i + 1] for i in range(len(non_missing) - 1))


@given(st.data())
def test_pandas_DataFrame_sort_values_property_data_is_permuted_not_changed(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    a = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    b = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    c = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))

    df = pandas.DataFrame({"a": a, "b": b, "c": c})
    result = df.sort_values(by="a")

    original_rows = sorted(df.itertuples(index=False, name=None))
    result_rows = sorted(result.itertuples(index=False, name=None))

    assert result.shape == df.shape
    assert list(result.columns) == list(df.columns)
    assert result_rows == original_rows


@given(st.data())
def test_pandas_DataFrame_sort_values_property_ignore_index(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    values = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    payload = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))

    original_index = list(range(1000, 1000 + n))
    df = pandas.DataFrame({"x": values, "payload": payload}, index=original_index)

    result_ignore = df.sort_values(by="x", ignore_index=True)
    result_keep = df.sort_values(by="x", ignore_index=False)

    assert result_ignore.shape == df.shape
    assert list(result_ignore.columns) == list(df.columns)
    assert list(result_ignore.index) == list(range(n))

    assert result_keep.shape == df.shape
    assert list(result_keep.columns) == list(df.columns)
    assert sorted(result_keep.index.tolist()) == sorted(original_index)


@given(st.data())
def test_pandas_DataFrame_sort_values_property_stable_equal_keys(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    keys = data.draw(st.lists(st.integers(min_value=-5, max_value=5), min_size=n, max_size=n))
    values = data.draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=n, max_size=n))
    ascending = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(["mergesort", "stable"]))

    df = pandas.DataFrame({"key": keys, "value": values, "original_position": list(range(n))})
    result = df.sort_values(by="key", ascending=ascending, kind=kind)

    for _, group in result.groupby("key", sort=False):
        positions = group["original_position"].tolist()
        assert positions == sorted(positions)

# End program