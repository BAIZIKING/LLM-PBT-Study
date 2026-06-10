from hypothesis import given, strategies as st
from collections import Counter
import pandas as pd

_NULL_KEY = object()


def _norm_key(x):
    """Normalize pandas null join keys so None/NaN compare as the same key."""
    try:
        if bool(pd.isna(x)):
            return _NULL_KEY
    except TypeError:
        pass
    return x


def _key_counts(keys):
    return Counter(_norm_key(k) for k in keys)


def _expected_row_count(how, left_keys, right_keys):
    if how == "cross":
        return len(left_keys) * len(right_keys)

    left_counts = _key_counts(left_keys)
    right_counts = _key_counts(right_keys)

    if how == "inner":
        return sum(left_counts[k] * right_counts[k] for k in left_counts.keys() & right_counts.keys())

    if how == "left":
        return sum(left_counts[k] * max(right_counts.get(k, 0), 1) for k in left_counts)

    if how == "right":
        return sum(right_counts[k] * max(left_counts.get(k, 0), 1) for k in right_counts)

    if how == "outer":
        total = 0
        for k in left_counts.keys() | right_counts.keys():
            if k in left_counts and k in right_counts:
                total += left_counts[k] * right_counts[k]
            elif k in left_counts:
                total += left_counts[k]
            else:
                total += right_counts[k]
        return total

    raise AssertionError(f"unexpected merge type: {how}")


def _expected_indicator_counts(how, left_keys, right_keys):
    if how == "cross":
        return {
            "left_only": 0,
            "right_only": 0,
            "both": len(left_keys) * len(right_keys),
        }

    left_counts = _key_counts(left_keys)
    right_counts = _key_counts(right_keys)

    both = sum(left_counts[k] * right_counts[k] for k in left_counts.keys() & right_counts.keys())
    left_only = sum(left_counts[k] for k in left_counts.keys() - right_counts.keys())
    right_only = sum(right_counts[k] for k in right_counts.keys() - left_counts.keys())

    return {
        "left_only": left_only if how in {"left", "outer"} else 0,
        "right_only": right_only if how in {"right", "outer"} else 0,
        "both": both,
    }


def _validate_ok(validate, left_keys, right_keys, how):
    if validate is None or validate in {"many_to_many", "m:m"}:
        return True

    if how == "cross":
        return True

    left_unique = all(v <= 1 for v in _key_counts(left_keys).values())
    right_unique = all(v <= 1 for v in _key_counts(right_keys).values())

    if validate in {"one_to_one", "1:1"}:
        return left_unique and right_unique
    if validate in {"one_to_many", "1:m"}:
        return left_unique
    if validate in {"many_to_one", "m:1"}:
        return right_unique

    return False


def _suffixed(column, suffix):
    return column if suffix is None else f"{column}{suffix}"


# Summary: Generates small random DataFrames with empty inputs, duplicate keys,
# null keys, overlapping non-key columns, several join-key specifications
# including column joins and index joins, all documented join types including
# cross joins, random suffixes, indicator settings, sort/copy flags, and validate
# modes. Properties checked: documented row cardinality for each join type,
# pandas null-key matching behavior, indicator-source counts, suffix handling for
# overlapping columns, and validate/suffix errors when the documented constraints
# are violated.
@given(st.data())
def test_pandas_merge(data):
    key_values = st.one_of(st.integers(-3, 3), st.none())
    payload_values = st.one_of(st.integers(-10, 10), st.text(max_size=3), st.none())

    join_style = data.draw(
        st.sampled_from(
            [
                "on",
                "left_on_right_on",
                "left_index_right_index",
                "left_index_right_on",
                "left_on_right_index",
                "cross",
            ]
        )
    )

    how = (
        "cross"
        if join_style == "cross"
        else data.draw(st.sampled_from(["inner", "left", "right", "outer"]))
    )

    n_left = data.draw(st.integers(0, 5))
    n_right = data.draw(st.integers(0, 5))

    left_keys = data.draw(st.lists(key_values, min_size=n_left, max_size=n_left))
    right_keys = data.draw(st.lists(key_values, min_size=n_right, max_size=n_right))

    left_v = data.draw(st.lists(payload_values, min_size=n_left, max_size=n_left))
    right_v = data.draw(st.lists(payload_values, min_size=n_right, max_size=n_right))

    suffixes = data.draw(
        st.sampled_from(
            [
                ("_x", "_y"),
                ("_left", "_right"),
                (None, "_right"),
                ("_left", None),
                (False, False),
            ]
        )
    )
    sort = data.draw(st.booleans())
    copy = data.draw(st.one_of(st.none(), st.booleans()))
    indicator = data.draw(st.sampled_from([False, True, "source"]))

    validate = data.draw(
        st.sampled_from(
            [None, "many_to_many", "m:m"]
            if how == "cross"
            else [None, "one_to_one", "1:1", "one_to_many", "1:m", "many_to_one", "m:1", "many_to_many", "m:m"]
        )
    )

    if join_style == "on":
        left = pd.DataFrame(
            {
                "k": pd.Series(left_keys, dtype=object),
                "v": left_v,
                "left_only": list(range(n_left)),
            }
        )
        right = pd.DataFrame(
            {
                "k": pd.Series(right_keys, dtype=object),
                "v": right_v,
                "right_only": list(range(n_right)),
            }
        )
        key_kwargs = {"on": "k"}

    elif join_style == "left_on_right_on":
        left = pd.DataFrame(
            {
                "lk": pd.Series(left_keys, dtype=object),
                "v": left_v,
                "left_only": list(range(n_left)),
            }
        )
        right = pd.DataFrame(
            {
                "rk": pd.Series(right_keys, dtype=object),
                "v": right_v,
                "right_only": list(range(n_right)),
            }
        )
        key_kwargs = {"left_on": "lk", "right_on": "rk"}

    elif join_style == "left_index_right_index":
        left = pd.DataFrame(
            {"v": left_v, "left_only": list(range(n_left))},
            index=pd.Index(left_keys, dtype=object, name="k"),
        )
        right = pd.DataFrame(
            {"v": right_v, "right_only": list(range(n_right))},
            index=pd.Index(right_keys, dtype=object, name="k"),
        )
        key_kwargs = {"left_index": True, "right_index": True}

    elif join_style == "left_index_right_on":
        left = pd.DataFrame(
            {"v": left_v, "left_only": list(range(n_left))},
            index=pd.Index(left_keys, dtype=object, name="k"),
        )
        right = pd.DataFrame(
            {
                "rk": pd.Series(right_keys, dtype=object),
                "v": right_v,
                "right_only": list(range(n_right)),
            }
        )
        key_kwargs = {"left_index": True, "right_on": "rk"}

    elif join_style == "left_on_right_index":
        left = pd.DataFrame(
            {
                "lk": pd.Series(left_keys, dtype=object),
                "v": left_v,
                "left_only": list(range(n_left)),
            }
        )
        right = pd.DataFrame(
            {"v": right_v, "right_only": list(range(n_right))},
            index=pd.Index(right_keys, dtype=object, name="k"),
        )
        key_kwargs = {"left_on": "lk", "right_index": True}

    else:
        left = pd.DataFrame({"v": left_v, "left_only": list(range(n_left))})
        right = pd.DataFrame({"v": right_v, "right_only": list(range(n_right))})
        key_kwargs = {}

    expected_suffix_error = suffixes == (False, False)
    expected_validate_error = not _validate_ok(validate, left_keys, right_keys, how)

    try:
        result = pd.merge(
            left,
            right,
            how=how,
            sort=sort,
            suffixes=suffixes,
            copy=copy,
            indicator=indicator,
            validate=validate,
            **key_kwargs,
        )
    except ValueError:
        assert expected_suffix_error or expected_validate_error
        return

    assert not expected_suffix_error
    assert not expected_validate_error
    assert isinstance(result, pd.DataFrame)

    assert len(result) == _expected_row_count(how, left_keys, right_keys)

    left_suffix, right_suffix = suffixes
    assert _suffixed("v", left_suffix) in result.columns
    assert _suffixed("v", right_suffix) in result.columns

    if indicator:
        indicator_name = "_merge" if indicator is True else indicator
        assert indicator_name in result.columns

        expected = _expected_indicator_counts(how, left_keys, right_keys)
        actual = result[indicator_name].value_counts().to_dict()

        assert actual.get("left_only", 0) == expected["left_only"]
        assert actual.get("right_only", 0) == expected["right_only"]
        assert actual.get("both", 0) == expected["both"]

# End program