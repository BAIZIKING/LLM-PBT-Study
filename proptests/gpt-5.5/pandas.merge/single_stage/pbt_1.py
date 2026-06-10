from hypothesis import given, strategies as st
from collections import Counter
import pandas as pd
from pandas.errors import MergeError

# Summary: Generate small left/right DataFrames with empty inputs, duplicate keys,
# mixed scalar key values, and null keys. Randomly choose valid merge configurations:
# common-column joins, different left/right key columns, index-index joins,
# index-column joins, and cross joins. Also vary how, sort, suffixes, copy,
# indicator, and validate. Properties checked: row counts match an independent
# join model including pandas' documented null-key matching behavior; indicator
# counts are correct; cross joins have cartesian-product size and order; suffixes
# are applied to overlapping columns; validate raises exactly when key uniqueness
# constraints are violated.
@given(st.data())
def test_pandas_merge(data):
    key_atom = st.one_of(
        st.integers(min_value=-2, max_value=2),
        st.text(min_size=0, max_size=2),
        st.none(),
        st.just(float("nan")),
    )
    payload_atom = st.one_of(
        st.integers(min_value=-10, max_value=10),
        st.text(min_size=0, max_size=3),
        st.none(),
    )

    n_left = data.draw(st.integers(min_value=0, max_value=5), label="n_left")
    n_right = data.draw(st.integers(min_value=0, max_value=5), label="n_right")

    left_keys = data.draw(
        st.lists(key_atom, min_size=n_left, max_size=n_left), label="left_keys"
    )
    right_keys = data.draw(
        st.lists(key_atom, min_size=n_right, max_size=n_right), label="right_keys"
    )

    left_v = data.draw(
        st.lists(payload_atom, min_size=n_left, max_size=n_left), label="left_v"
    )
    right_v = data.draw(
        st.lists(payload_atom, min_size=n_right, max_size=n_right), label="right_v"
    )

    how = data.draw(
        st.sampled_from(["left", "right", "outer", "inner", "cross"]), label="how"
    )
    sort = data.draw(st.booleans(), label="sort")
    suffixes = data.draw(
        st.sampled_from(
            [
                ("_x", "_y"),
                ("_left", "_right"),
                ("_L", "_R"),
                (None, "_right"),
                ("_left", None),
            ]
        ),
        label="suffixes",
    )
    copy = data.draw(st.one_of(st.none(), st.booleans()), label="copy")
    indicator = data.draw(
        st.one_of(st.booleans(), st.sampled_from(["__source"])), label="indicator"
    )

    if how == "cross":
        validate = data.draw(
            st.sampled_from([None, "many_to_many", "m:m"]), label="validate"
        )
    else:
        validate = data.draw(
            st.sampled_from(
                [
                    None,
                    "one_to_one",
                    "1:1",
                    "one_to_many",
                    "1:m",
                    "many_to_one",
                    "m:1",
                    "many_to_many",
                    "m:m",
                ]
            ),
            label="validate",
        )

    def key_series(name, values):
        return pd.Series(values, dtype="object", name=name)

    def key_index(name, values):
        return pd.Index(values, dtype="object", name=name)

    if how == "cross":
        left = pd.DataFrame(
            {
                "v": left_v,
                "lpos": list(range(n_left)),
            }
        )
        right = pd.DataFrame(
            {
                "v": right_v,
                "rpos": list(range(n_right)),
            }
        )
        join_kwargs = {}
    else:
        join_kind = data.draw(
            st.sampled_from(
                [
                    "on",
                    "left_on_right_on",
                    "index_index",
                    "left_index_right_on",
                    "left_on_right_index",
                ]
            ),
            label="join_kind",
        )

        if join_kind == "on":
            left = pd.DataFrame(
                {
                    "k": key_series("k", left_keys),
                    "v": left_v,
                    "lpos": list(range(n_left)),
                }
            )
            right = pd.DataFrame(
                {
                    "k": key_series("k", right_keys),
                    "v": right_v,
                    "rpos": list(range(n_right)),
                }
            )
            join_kwargs = {"on": "k"}

        elif join_kind == "left_on_right_on":
            left = pd.DataFrame(
                {
                    "lk": key_series("lk", left_keys),
                    "v": left_v,
                    "lpos": list(range(n_left)),
                }
            )
            right = pd.DataFrame(
                {
                    "rk": key_series("rk", right_keys),
                    "v": right_v,
                    "rpos": list(range(n_right)),
                }
            )
            join_kwargs = {"left_on": "lk", "right_on": "rk"}

        elif join_kind == "index_index":
            left = pd.DataFrame({"v": left_v, "lpos": list(range(n_left))})
            right = pd.DataFrame({"v": right_v, "rpos": list(range(n_right))})
            left.index = key_index("k", left_keys)
            right.index = key_index("k", right_keys)
            join_kwargs = {"left_index": True, "right_index": True}

        elif join_kind == "left_index_right_on":
            left = pd.DataFrame({"v": left_v, "lpos": list(range(n_left))})
            right = pd.DataFrame(
                {
                    "rk": key_series("rk", right_keys),
                    "v": right_v,
                    "rpos": list(range(n_right)),
                }
            )
            left.index = key_index("k", left_keys)
            join_kwargs = {"left_index": True, "right_on": "rk"}

        else:
            left = pd.DataFrame(
                {
                    "lk": key_series("lk", left_keys),
                    "v": left_v,
                    "lpos": list(range(n_left)),
                }
            )
            right = pd.DataFrame({"v": right_v, "rpos": list(range(n_right))})
            right.index = key_index("k", right_keys)
            join_kwargs = {"left_on": "lk", "right_index": True}

    def normalized_key(value):
        if pd.isna(value):
            return ("<NULL>",)
        return ("<VALUE>", value)

    def is_unique_for_merge(keys):
        normalized = [normalized_key(k) for k in keys]
        return len(normalized) == len(set(normalized))

    def validate_should_fail():
        if validate in (None, "many_to_many", "m:m"):
            return False
        left_unique = is_unique_for_merge(left_keys)
        right_unique = is_unique_for_merge(right_keys)
        if validate in ("one_to_one", "1:1"):
            return not (left_unique and right_unique)
        if validate in ("one_to_many", "1:m"):
            return not left_unique
        if validate in ("many_to_one", "m:1"):
            return not right_unique
        raise AssertionError(f"unexpected validate value: {validate!r}")

    merge_kwargs = dict(
        how=how,
        sort=sort,
        suffixes=suffixes,
        copy=copy,
        indicator=indicator,
        validate=validate,
        **join_kwargs,
    )

    if validate_should_fail():
        try:
            pd.merge(left, right, **merge_kwargs)
        except (MergeError, ValueError):
            return
        raise AssertionError(f"validate={validate!r} should have rejected the merge")

    result = pd.merge(left, right, **merge_kwargs)

    def expected_source_counts():
        if how == "cross":
            return {
                "left_only": 0,
                "right_only": 0,
                "both": n_left * n_right,
            }

        left_counts = Counter(normalized_key(k) for k in left_keys)
        right_counts = Counter(normalized_key(k) for k in right_keys)
        all_keys = set(left_counts) | set(right_counts)

        expected = {"left_only": 0, "right_only": 0, "both": 0}

        for key in all_keys:
            left_count = left_counts.get(key, 0)
            right_count = right_counts.get(key, 0)

            if how == "inner":
                if left_count and right_count:
                    expected["both"] += left_count * right_count

            elif how == "left":
                if right_count:
                    expected["both"] += left_count * right_count
                else:
                    expected["left_only"] += left_count

            elif how == "right":
                if left_count:
                    expected["both"] += left_count * right_count
                else:
                    expected["right_only"] += right_count

            elif how == "outer":
                if left_count and right_count:
                    expected["both"] += left_count * right_count
                elif left_count:
                    expected["left_only"] += left_count
                else:
                    expected["right_only"] += right_count

            else:
                raise AssertionError(f"unexpected how value: {how!r}")

        return expected

    expected_counts = expected_source_counts()
    assert len(result) == sum(expected_counts.values())

    left_suffix, right_suffix = suffixes
    expected_left_v = "v" if left_suffix is None else f"v{left_suffix}"
    expected_right_v = "v" if right_suffix is None else f"v{right_suffix}"
    assert expected_left_v in result.columns
    assert expected_right_v in result.columns
    assert expected_left_v != expected_right_v

    if indicator:
        indicator_name = "_merge" if indicator is True else indicator
        assert indicator_name in result.columns
        assert isinstance(result[indicator_name].dtype, pd.CategoricalDtype)
        assert set(result[indicator_name].cat.categories) == {
            "left_only",
            "right_only",
            "both",
        }

        observed_counts = result[indicator_name].value_counts().to_dict()
        assert int(observed_counts.get("left_only", 0)) == expected_counts["left_only"]
        assert int(observed_counts.get("right_only", 0)) == expected_counts["right_only"]
        assert int(observed_counts.get("both", 0)) == expected_counts["both"]

    if how == "cross":
        assert result["lpos"].tolist() == [
            left_pos for left_pos in range(n_left) for _ in range(n_right)
        ]
        assert result["rpos"].tolist() == list(range(n_right)) * n_left

# End program