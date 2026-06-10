from hypothesis import given, strategies as st
import pandas


@given(st.data())
def test_pandas_DataFrame_sort_values_preserves_rows_as_permutation(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    value_strategy = st.one_of(st.integers(min_value=-10_000, max_value=10_000), st.none())

    df = pandas.DataFrame(
        {
            "a": data.draw(st.lists(value_strategy, min_size=n, max_size=n)),
            "b": data.draw(st.lists(value_strategy, min_size=n, max_size=n)),
            "c": data.draw(st.lists(value_strategy, min_size=n, max_size=n)),
        }
    )

    by = data.draw(st.sampled_from(["a", ["a", "b"]]))
    if isinstance(by, list):
        ascending = data.draw(st.lists(st.booleans(), min_size=len(by), max_size=len(by)))
    else:
        ascending = data.draw(st.booleans())

    result = df.sort_values(by=by, ascending=ascending)

    pandas.testing.assert_frame_equal(
        result.sort_index(),
        df.sort_index(),
    )


@given(st.data())
def test_pandas_DataFrame_sort_values_output_is_ordered_by_keys(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    df = pandas.DataFrame(
        {
            "x": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
            "y": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
        }
    )

    ascending = data.draw(st.lists(st.booleans(), min_size=2, max_size=2))
    use_key = data.draw(st.booleans())

    if use_key:
        result = df.sort_values(by=["x", "y"], ascending=ascending, key=lambda col: -col)
    else:
        result = df.sort_values(by=["x", "y"], ascending=ascending)

    def transformed(value):
        return -value if use_key else value

    records = list(result[["x", "y"]].itertuples(index=False, name=None))

    for left, right in zip(records, records[1:]):
        for left_value, right_value, is_ascending in (
            (transformed(left[0]), transformed(right[0]), ascending[0]),
            (transformed(left[1]), transformed(right[1]), ascending[1]),
        ):
            if left_value == right_value:
                continue
            if is_ascending:
                assert left_value < right_value
            else:
                assert left_value > right_value
            break


@given(st.data())
def test_pandas_DataFrame_sort_values_places_missing_values_correctly(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    df = pandas.DataFrame(
        {
            "a": data.draw(
                st.lists(
                    st.one_of(st.integers(min_value=-10_000, max_value=10_000), st.none()),
                    min_size=n,
                    max_size=n,
                )
            ),
            "payload": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
        }
    )

    na_position = data.draw(st.sampled_from(["first", "last"]))
    ascending = data.draw(st.booleans())

    result = df.sort_values(by="a", ascending=ascending, na_position=na_position)
    missing_mask = result["a"].isna().tolist()
    missing_count = sum(missing_mask)

    if na_position == "first":
        assert all(missing_mask[:missing_count])
        assert not any(missing_mask[missing_count:])
    else:
        non_missing_count = len(missing_mask) - missing_count
        assert not any(missing_mask[:non_missing_count])
        assert all(missing_mask[non_missing_count:])


@given(st.data())
def test_pandas_DataFrame_sort_values_ignore_index_controls_result_index(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    index = data.draw(
        st.lists(
            st.integers(min_value=-100_000, max_value=100_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )

    df = pandas.DataFrame(
        {
            "a": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
            "b": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
        },
        index=index,
    )

    preserved = df.sort_values(by="a", ignore_index=False, kind="mergesort")
    ignored = df.sort_values(by="a", ignore_index=True, kind="mergesort")

    assert set(preserved.index) == set(df.index)
    assert len(preserved.index) == len(df.index)
    assert list(ignored.index) == list(range(n))

    pandas.testing.assert_frame_equal(
        preserved.sort_index(),
        df.sort_index(),
    )


@given(st.data())
def test_pandas_DataFrame_sort_values_inplace_returns_none_and_mutates(data):
    n = data.draw(st.integers(min_value=0, max_value=30))
    df = pandas.DataFrame(
        {
            "a": data.draw(
                st.lists(
                    st.one_of(st.integers(min_value=-10_000, max_value=10_000), st.none()),
                    min_size=n,
                    max_size=n,
                )
            ),
            "b": data.draw(
                st.lists(st.integers(min_value=-10_000, max_value=10_000), min_size=n, max_size=n)
            ),
        }
    )

    expected = df.sort_values(by="a", kind="mergesort")
    mutated = df.copy(deep=True)

    returned = mutated.sort_values(by="a", kind="mergesort", inplace=True)

    assert returned is None
    pandas.testing.assert_frame_equal(mutated, expected)


# End program