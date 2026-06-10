from hypothesis import given, strategies as st
import math
import numpy as np
import pandas as pd

# Summary: Draw one of several input "kinds" (scalar, ndarray, Series,
# DataFrame, Index) built from a mix of valid values and recognized missing
# values (None, np.nan, pd.NA, pd.NaT). For each, keep a parallel ground-truth
# of which entries are missing, then check the return type contract, the
# correctness of detected missingness, and the inverse relationship with notna.
@given(st.data())
def test_pandas_isna(data):
    MISSING = [None, np.nan, float("nan"), pd.NA, pd.NaT]

    def is_missing(v):
        # Mirror pandas' notion of "missing" for the values we generate.
        if v is None or v is pd.NA or v is pd.NaT:
            return True
        if isinstance(v, float) and math.isnan(v):
            return True
        return False

    valid_values = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=True, width=64),
        st.text(min_size=0, max_size=5),
        st.booleans(),
    )
    cell = st.one_of(valid_values, st.sampled_from(MISSING))

    kind = data.draw(st.sampled_from(["scalar", "ndarray", "series", "dataframe", "index"]))

    if kind == "scalar":
        value = data.draw(cell)
        result = pd.isna(value)
        # Scalar input -> scalar boolean.
        assert np.isscalar(result) or isinstance(result, (bool, np.bool_))
        assert bool(result) == is_missing(value)
        # Inverse of notna.
        assert bool(result) == (not bool(pd.notna(value)))

    elif kind == "ndarray":
        # Numeric ndarray: missing means NaN.
        n = data.draw(st.integers(min_value=1, max_value=20))
        floats = data.draw(
            st.lists(
                st.one_of(
                    st.floats(allow_nan=False, allow_infinity=True, width=64),
                    st.just(np.nan),
                ),
                min_size=n,
                max_size=n,
            )
        )
        arr = np.array(floats, dtype=float)
        result = pd.isna(arr)
        # ndarray input -> ndarray of bool, same shape.
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == arr.shape
        expected = np.array([math.isnan(x) for x in floats])
        assert np.array_equal(result, expected)
        # Inverse of notna.
        assert np.array_equal(result, ~pd.notna(arr))

    elif kind == "series":
        n = data.draw(st.integers(min_value=1, max_value=15))
        values = data.draw(st.lists(cell, min_size=n, max_size=n))
        s = pd.Series(values, dtype=object)
        result = pd.isna(s)
        # Series input -> Series of bool, same index/length.
        assert isinstance(result, pd.Series)
        assert result.dtype == bool
        assert list(result.index) == list(s.index)
        expected = [is_missing(v) for v in values]
        assert list(result) == expected
        # Inverse of notna.
        assert list(result) == list(~pd.notna(s))

    elif kind == "dataframe":
        nrows = data.draw(st.integers(min_value=1, max_value=6))
        ncols = data.draw(st.integers(min_value=1, max_value=4))
        rows = [
            data.draw(st.lists(cell, min_size=ncols, max_size=ncols))
            for _ in range(nrows)
        ]
        df = pd.DataFrame(rows, dtype=object)
        result = pd.isna(df)
        # DataFrame input -> DataFrame of bool, same shape.
        assert isinstance(result, pd.DataFrame)
        assert result.shape == df.shape
        assert (result.dtypes == bool).all()
        expected = [[is_missing(v) for v in row] for row in rows]
        assert result.values.tolist() == expected
        # Inverse of notna.
        assert (result.values == (~pd.notna(df)).values).all()

    else:  # index
        n = data.draw(st.integers(min_value=1, max_value=12))
        # Datetime-like Index where None becomes NaT.
        choices = ["2017-07-05", "2017-07-06", "2017-07-08", None]
        values = data.draw(
            st.lists(st.sampled_from(choices), min_size=n, max_size=n)
        )
        index = pd.DatetimeIndex(values)
        result = pd.isna(index)
        # Index input -> ndarray of bool.
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == (len(index),)
        expected = np.array([v is None for v in values])
        assert np.array_equal(result, expected)
        # Inverse of notna.
        assert np.array_equal(result, ~pd.notna(index))
# End program