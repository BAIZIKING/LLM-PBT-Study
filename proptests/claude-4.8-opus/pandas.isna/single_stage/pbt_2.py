from hypothesis import given, strategies as st
import math
import numpy as np
import pandas as pd

# Summary: Generate scalars and array-likes (ndarray/Series/DataFrame/Index)
# composed of a mix of missing sentinels (np.nan, None, pd.NA, pd.NaT) and
# concrete values (ints, floats, bools, strings). Verify that isna returns the
# correct type (scalar vs array-like), correctly flags known missing/non-missing
# values, and is the exact boolean inverse of pd.notna.
@given(st.data())
def test_pandas_isna(data):
    # Values that pandas treats as missing
    missing_values = st.sampled_from([np.nan, None, pd.NA, pd.NaT, float("nan")])
    # Values that are definitely NOT missing
    concrete_values = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e6, max_value=1e6),
        st.booleans(),
        st.text(min_size=1, max_size=5),
    )
    any_value = st.one_of(missing_values, concrete_values)

    def is_missing_sentinel(v):
        if v is None or v is pd.NA or v is pd.NaT:
            return True
        if isinstance(v, float) and math.isnan(v):
            return True
        return False

    kind = data.draw(st.sampled_from(["scalar", "ndarray", "series", "dataframe", "index"]))

    if kind == "scalar":
        obj = data.draw(any_value)
        result = pd.isna(obj)
        # Property 1: scalar input -> scalar boolean
        assert isinstance(result, (bool, np.bool_))
        # Property 3: correctness for known scalars
        assert bool(result) == is_missing_sentinel(obj)
        # Property 4: inverse of notna
        assert bool(result) == (not bool(pd.notna(obj)))

    else:
        values = data.draw(st.lists(any_value, min_size=1, max_size=8))
        expected = [is_missing_sentinel(v) for v in values]

        if kind == "ndarray":
            obj = np.array(values, dtype=object)
            result = pd.isna(obj)
            assert isinstance(result, np.ndarray)
            assert result.dtype == bool
            assert result.shape == obj.shape
            assert list(result) == expected
            # Inverse of notna
            assert list(result) == list(~pd.notna(obj))

        elif kind == "series":
            obj = pd.Series(values, dtype=object)
            result = pd.isna(obj)
            assert isinstance(result, pd.Series)
            assert result.dtype == bool
            assert list(result) == expected
            assert (result == ~pd.notna(obj)).all()

        elif kind == "dataframe":
            obj = pd.DataFrame({"col": values}, dtype=object)
            result = pd.isna(obj)
            assert isinstance(result, pd.DataFrame)
            assert list(result["col"]) == expected
            assert (result == ~pd.notna(obj)).all().all()

        elif kind == "index":
            obj = pd.Index(values, dtype=object)
            result = pd.isna(obj)
            assert isinstance(result, np.ndarray)
            assert result.dtype == bool
            assert list(result) == expected
            assert list(result) == list(~pd.notna(obj))
# End program