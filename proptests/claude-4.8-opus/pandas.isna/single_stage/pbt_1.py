from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate scalars (including missing-value markers like np.nan, None,
# pd.NA, pd.NaT), and array-likes/containers (np.ndarray, Series, DataFrame, Index)
# built from those scalars. Then verify: scalar->scalar bool with correct missing
# detection; containers preserve type/shape with bool values; and isna is the
# boolean inverse of notna in all cases.
@given(st.data())
def test_pandas_isna():
    data = st.data()

    # Markers that ARE considered missing by pandas
    missing_markers = st.sampled_from([np.nan, None, pd.NA, pd.NaT, float("nan")])
    # Values that are NOT missing
    non_missing = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(min_size=0, max_size=5),
        st.booleans(),
    )
    scalars = st.one_of(missing_markers, non_missing)

    def is_missing_scalar(v):
        # Reference implementation for a single scalar
        if v is None or v is pd.NA or v is pd.NaT:
            return True
        if isinstance(v, float):
            return np.isnan(v)
        return False

    kind = data.example() if False else None  # placeholder to keep flake quiet

    choice = st.integers(min_value=0, max_value=4)
    c = st_draw = None

    # Use the hypothesis data object correctly:
    # We'll redefine using the injected 'data' strategy properly.
    raise_marker = None  # not used


@given(st.data())
def test_pandas_isna(data):
    missing_markers = st.sampled_from([np.nan, None, pd.NA, pd.NaT, float("nan")])
    non_missing = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(min_size=0, max_size=5),
        st.booleans(),
    )
    scalars = st.one_of(missing_markers, non_missing)

    def is_missing_scalar(v):
        if v is None or v is pd.NA or v is pd.NaT:
            return True
        if isinstance(v, float):
            return np.isnan(v)
        return False

    kind = data.draw(st.integers(min_value=0, max_value=4))

    if kind == 0:
        # Scalar input
        obj = data.draw(scalars)
        result = pd.isna(obj)
        # Property 1: scalar -> scalar bool
        assert np.isscalar(result) or isinstance(result, (bool, np.bool_))
        assert isinstance(bool(result), bool)
        # Property 2: correct missing detection
        assert bool(result) == is_missing_scalar(obj)
        # Property 4: inverse of notna
        assert bool(result) == (not bool(pd.notna(obj)))

    elif kind == 1:
        # 1-D ndarray (object dtype to allow mixed/missing)
        lst = data.draw(st.lists(scalars, min_size=1, max_size=8))
        arr = np.array(lst, dtype=object)
        result = pd.isna(arr)
        # Property 3: ndarray -> ndarray of bool, same shape
        assert isinstance(result, np.ndarray)
        assert result.shape == arr.shape
        assert result.dtype == bool
        # Property 2: elementwise correctness
        expected = np.array([is_missing_scalar(v) for v in lst], dtype=bool)
        assert np.array_equal(result, expected)
        # Property 4: inverse of notna
        assert np.array_equal(result, ~pd.notna(arr))

    elif kind == 2:
        # pandas Series
        lst = data.draw(st.lists(scalars, min_size=1, max_size=8))
        ser = pd.Series(lst, dtype=object)
        result = pd.isna(ser)
        # Property 3: Series -> Series of bool, same shape/index
        assert isinstance(result, pd.Series)
        assert result.shape == ser.shape
        assert result.dtype == bool
        assert list(result.index) == list(ser.index)
        # Property 2: elementwise correctness
        expected = [is_missing_scalar(v) for v in lst]
        assert list(result) == expected
        # Property 4: inverse of notna
        assert (result == ~pd.notna(ser)).all()

    elif kind == 3:
        # pandas Index
        lst = data.draw(st.lists(scalars, min_size=1, max_size=8))
        idx = pd.Index(lst, dtype=object)
        result = pd.isna(idx)
        # Property 3: Index -> ndarray of bool, same length
        assert isinstance(result, np.ndarray)
        assert result.shape == (len(idx),)
        assert result.dtype == bool
        # Property 2: elementwise correctness
        expected = np.array([is_missing_scalar(v) for v in lst], dtype=bool)
        assert np.array_equal(result, expected)
        # Property 4: inverse of notna
        assert np.array_equal(result, ~np.asarray(pd.notna(idx)))

    else:
        # pandas DataFrame
        n_rows = data.draw(st.integers(min_value=1, max_value=5))
        n_cols = data.draw(st.integers(min_value=1, max_value=4))
        rows = [
            [data.draw(scalars) for _ in range(n_cols)]
            for _ in range(n_rows)
        ]
        df = pd.DataFrame(rows, dtype=object)
        result = pd.isna(df)
        # Property 3: DataFrame -> DataFrame of bool, same shape
        assert isinstance(result, pd.DataFrame)
        assert result.shape == df.shape
        assert (result.dtypes == bool).all()
        # Property 2: elementwise correctness
        for i in range(n_rows):
            for j in range(n_cols):
                assert bool(result.iloc[i, j]) == is_missing_scalar(rows[i][j])
        # Property 4: inverse of notna
        assert (result == ~pd.notna(df)).all().all()
# End program