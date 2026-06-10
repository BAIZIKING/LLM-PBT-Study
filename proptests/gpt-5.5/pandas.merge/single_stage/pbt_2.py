from hypothesis import given, strategies as st
import numpy as np
import pandas as pd
from collections import Counter
from pandas.errors import MergeError

# Summary: Generate small left/right DataFrames with empty/non-empty sizes,
# duplicate keys, missing keys, custom non-Range indexes, overlapping columns,
# all merge modes, column/index/array-like join specifications, suffix variants,
# indicator variants, copy/sort values, and validate values.  The test checks
# database-style row-count semantics, pandas' documented NULL-key matching,
# validate enforcement, indicator contents, cross-join size, and that column
# joins ignore the original indexes.
@given(st.data())
def test_pandas_merge(data):
    key_values = st.one_of(st.none(), st.sampled_from(["", "a", "b", "c"]))
    n_left = data.draw(st.integers(min_value=0, max_value=5))
    n_right = data.draw(st.integers(min_value=0, max_value=5))

    def draw_keys(n):
        return data.draw(st.lists(key_values, min_size=n, max_size=n))

    left_col_keys = draw_keys(n_left)
    right_col_keys = draw_keys(n_right)
    left_index_keys = draw_keys(n_left)
    right_index_keys = draw_keys(n_right)

    left_overlap = data.draw(st.lists(st.integers(-10, 10), min_size=n_left, max_size=n_left))
    right_overlap = data.draw(st.lists(st.integers(-10, 10), min_size=n_right, max_size=n_right))
    left_values = data.draw(st.lists(st.integers(-10, 10), min_size=n_left, max_size=n_left))
    right_values = data.draw(st.lists(st.integers(-10, 10), min_size=n_right, max_size=n_right))

    how = data.draw(st.sampled_from(["left", "right", "outer", "inner", "cross"]))

    on = None
    left_on = None
    right_on = None
    left_index = False
    right_index = False

    if how == "cross":
        mode = "cross"
        left = pd.DataFrame({"overlap": left_overlap, "lval": left_values})
        right = pd.DataFrame({"overlap": right_overlap, "rval": right_values})
        left_keys_for_count = None
        right_keys_for_count = None
    else:
        mode = data.draw(
            st.sampled_from(
                [
                    "same_column_on",
                    "different_column_on",
                    "left_index_right_column",
                    "left_column_right_index",
                    "index_index",
                    "array_like_keys",
                ]
            )
        )

        if mode == "same_column_on":
            left = pd.DataFrame(
                {
                    "k": pd.Series(left_col_keys, dtype=object),
                    "overlap": left_overlap,
                    "lval": left_values,
                }
            )
            right = pd.DataFrame(
                {
                    "k": pd.Series(right_col_keys, dtype=object),
                    "overlap": right_overlap,
                    "rval": right_values,
                }
            )
            on = data.draw(st.sampled_from(["k", ["k"]]))
            left_keys_for_count = left_col_keys
            right_keys_for_count = right_col_keys

        elif mode == "different_column_on":
            left = pd.DataFrame(
                {
                    "lk": pd.Series(left_col_keys, dtype=object),
                    "overlap": left_overlap,
                    "lval": left_values,
                }
            )
            right = pd.DataFrame(
                {
                    "rk": pd.Series(right_col_keys, dtype=object),
                    "overlap": right_overlap,
                    "rval": right_values,
                }
            )
            left_on = data.draw(st.sampled_from(["lk", ["lk"]]))
            right_on = data.draw(st.sampled_from(["rk", ["rk"]]))
            left_keys_for_count = left_col_keys
            right_keys_for_count = right_col_keys

        elif mode == "left_index_right_column":
            left = pd.DataFrame({"overlap": left_overlap, "lval": left_values})
            right = pd.DataFrame(
                {
                    "rk": pd.Series(right_col_keys, dtype=object),
                    "overlap": right_overlap,
                    "rval": right_values,
                }
            )
            left_index = True
            right_on = data.draw(st.sampled_from(["rk", ["rk"]]))
            left_keys_for_count = left_index_keys
            right_keys_for_count = right_col_keys

        elif mode == "left_column_right_index":
            left = pd.DataFrame(
                {
                    "lk": pd.Series(left_col_keys, dtype=object),
                    "overlap": left_overlap,
                    "lval": left_values,
                }
            )
            right = pd.DataFrame({"overlap": right_overlap, "rval": right_values})
            left_on = data.draw(st.sampled_from(["lk", ["lk"]]))
            right_index = True
            left_keys_for_count = left_col_keys
            right_keys_for_count = right_index_keys

        elif mode == "index_index":
            left = pd.DataFrame({"overlap": left_overlap, "lval": left_values})
            right = pd.DataFrame({"overlap": right_overlap, "rval": right_values})
            left_index = True
            right_index = True
            left_keys_for_count = left_index_keys
            right_keys_for_count = right_index_keys

        else:
            left = pd.DataFrame({"overlap": left_overlap, "lval": left_values})
            right = pd.DataFrame({"overlap": right_overlap, "rval": right_values})
            left_on = np.asarray(left_col_keys, dtype=object)
            right_on = np.asarray(right_col_keys, dtype=object)
            left_keys_for_count = left_col_keys
            right_keys_for_count = right_col_keys

    left.index = pd.Index(left_index_keys, dtype=object, name="idx")
    right.index = pd.Index(right_index_keys, dtype=object, name="idx")

    sort = data.draw(st.booleans())
    suffixes = data.draw(
        st.sampled_from(
            [
                ("_x", "_y"),
                ("_left", "_right"),
                (None, "_right"),
                ("_left", None),
            ]
        )
    )
    copy = data.draw(st.sampled_from([None, True, False]))
    indicator = data.draw(st.one_of(st.booleans(), st.sampled_from(["source", "_source"])))

    validate_options = [
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
    validate = None if how == "cross" else data.draw(st.sampled_from(validate_options))

    def norm_key(x):
        return ("<NA>",) if pd.isna(x) else ("<VALUE>", x)

    def counts(keys):
        return Counter(norm_key(k) for k in keys)

    def is_unique(keys):
        c = counts(keys)
        return all(v == 1 for v in c.values())

    if how == "cross":
        expected_rows = n_left * n_right
        validation_ok = True
    else:
        left_counts = counts(left_keys_for_count)
        right_counts = counts(right_keys_for_count)
        all_keys = set(left_counts) | set(right_counts)
        common_keys = set(left_counts) & set(right_counts)

        if how == "inner":
            expected_rows = sum(left_counts[k] * right_counts[k] for k in common_keys)
        elif how == "left":
            expected_rows = sum(
                left_counts[k] * (right_counts[k] if k in right_counts else 1)
                for k in left_counts
            )
        elif how == "right":
            expected_rows = sum(
                right_counts[k] * (left_counts[k] if k in left_counts else 1)
                for k in right_counts
            )
        else:
            expected_rows = sum(
                left_counts[k] * right_counts[k]
                if k in left_counts and k in right_counts
                else left_counts.get(k, 0) + right_counts.get(k, 0)
                for k in all_keys
            )

        left_unique = is_unique(left_keys_for_count)
        right_unique = is_unique(right_keys_for_count)
        validation_ok = (
            validate is None
            or validate in ("many_to_many", "m:m")
            or (validate in ("one_to_one", "1:1") and left_unique and right_unique)
            or (validate in ("one_to_many", "1:m") and left_unique)
            or (validate in ("many_to_one", "m:1") and right_unique)
        )

    try:
        result = pd.merge(
            left,
            right,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            sort=sort,
            suffixes=suffixes,
            copy=copy,
            indicator=indicator,
            validate=validate,
        )
    except Exception as exc:
        if validate is not None and not validation_ok:
            assert isinstance(exc, MergeError)
            return
        raise

    assert validation_ok
    assert isinstance(result, pd.DataFrame)
    assert len(result) == expected_rows
    assert result.columns.is_unique

    indicator_name = "_merge" if indicator is True else indicator if isinstance(indicator, str) else None
    if indicator_name is not None:
        assert indicator_name in result.columns
        assert isinstance(result[indicator_name].dtype, pd.CategoricalDtype)

        observed = set(result[indicator_name].astype(str))
        if how in ("inner", "cross"):
            assert observed <= {"both"}
        elif how == "left":
            assert observed <= {"left_only", "both"}
        elif how == "right":
            assert observed <= {"right_only", "both"}
        else:
            assert observed <= {"left_only", "right_only", "both"}
    else:
        assert "_merge" not in result.columns

    if mode in {"same_column_on", "different_column_on", "array_like_keys", "cross"}:
        assert isinstance(result.index, pd.RangeIndex)
        assert list(result.index) == list(range(len(result)))
# End program