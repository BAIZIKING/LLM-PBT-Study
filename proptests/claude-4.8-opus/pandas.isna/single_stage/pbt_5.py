from hypothesis import given, strategies as st
import numpy as np
import pandas as pd
import math

# Summary: Generate scalars (regular values + missing sentinels like None,
# np.nan, pd.NA, pd.NaT) and array-likes built from those scalars wrapped in
# various containers (list, ndarray, Series, Index, DataFrame). Check the
# return-type contract, correct missing-value detection, the notna inverse
# relationship, and shape preservation.
@given(st.data())
def test_pandas_isna():
    # Strategy for "missing" sentinel values
    missing_values = st.sampled_from([None, np.nan, float("nan"), pd.NA, pd.NaT])

    # Strategy for ordinary (non-missing) values
    normal_values = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e6, max_value=1e6),
        st.booleans(),
        st.text(min_size=0, max_size=5),
    )

    scalar_strategy = st.one_of(missing_values, normal_values)

    # A reference predicate: is this scalar a "missing" value?
    def is_missing_scalar(v):
        if v is None:
            return True
        if v is pd.NA:
            return True
        if v is pd.NaT:
            return True
        if isinstance(v, float) and math.isnan(v):
            return True
        return False

    data = st.data()

    # Decide whether to test a scalar or an array-like input
    use_scalar = st.booleans()

    if data.draw(use_scalar):
        # ---------- Scalar case ----------
        obj = data.draw(scalar_strategy)
        result = pd.isna(obj)

        # Property 1: scalar input -> scalar bool
        assert isinstance(result, (bool, np.bool_)), (
            f"Expected scalar bool for {obj!r}, got {type(result)}"
        )

        # Property 2: correctness
        expected = is_missing_scalar(obj)
        assert bool(result) == expected, (
            f"isna({obj!r}) returned {result}, expected {expected}"
        )

        # Property 3: inverse of notna
        assert bool(pd.notna(obj)) == (not bool(result))

    else:
        # ---------- Array-like case ----------
        elems = data.draw(st.lists(scalar_strategy, min_size=0, max_size=8))
        expected_flags = [is_missing_scalar(v) for v in elems]

        container = data.draw(
            st.sampled_from(["list", "ndarray", "series", "index"])
        )

        if container == "list":
            obj = list(elems)
            result = pd.isna(obj)
            assert isinstance(result, np.ndarray)
            assert result.dtype == bool
            actual = list(result)

        elif container == "ndarray":
            obj = np.array(elems, dtype=object)
            result = pd.isna(obj)
            assert isinstance(result, np.ndarray)
            # Property 4: shape preserved
            assert result.shape == obj.shape
            assert result.dtype == bool
            actual = list(result)

        elif container == "series":
            obj = pd.Series(elems, dtype=object)
            result = pd.isna(obj)
            # Property 1 (container contract): Series -> Series
            assert isinstance(result, pd.Series)
            assert result.dtype == bool
            assert len(result) == len(obj)
            # Inverse relationship
            notna_result = pd.notna(obj)
            assert (result == ~notna_result).all()
            actual = list(result)

        else:  # index
            obj = pd.Index(elems, dtype=object)
            result = pd.isna(obj)
            # Index -> ndarray of bools
            assert isinstance(result, np.ndarray)
            assert result.dtype == bool
            assert result.shape == (len(elems),)
            actual = list(result)

        # Property 2: correctness elementwise
        assert [bool(x) for x in actual] == expected_flags, (
            f"Mismatch for {container}: got {actual}, expected {expected_flags}"
        )
# End program