from hypothesis import given, strategies as st
import hypothesis.extra.numpy as hnp
import numpy as np
import pandas as pd
import math


def scalar_strategy():
    missing = st.sampled_from([np.nan, None, pd.NA, pd.NaT, float("nan")])
    non_missing = st.one_of(
        st.integers(min_value=-(10**9), max_value=10**9),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e9, max_value=1e9),
        st.text(max_size=10),
        st.booleans(),
    )
    return st.one_of(missing, non_missing)


def is_missing_scalar(x):
    if x is None or x is pd.NA or x is pd.NaT:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    return False


def float_array_1d():
    elements = st.floats(allow_nan=True, allow_infinity=False,
                         min_value=-1e9, max_value=1e9)
    return hnp.arrays(
        dtype=np.float64,
        shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=0, max_side=6),
        elements=elements,
    )


def float_array_2d():
    elements = st.floats(allow_nan=True, allow_infinity=False,
                         min_value=-1e9, max_value=1e9)
    return hnp.arrays(
        dtype=np.float64,
        shape=hnp.array_shapes(min_dims=2, max_dims=2, min_side=0, max_side=5),
        elements=elements,
    )


def object_array_1d():
    elements = st.one_of(
        st.none(),
        st.text(max_size=5),
        st.integers(min_value=-1000, max_value=1000),
        st.just(np.nan),
    )
    return hnp.arrays(
        dtype=object,
        shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=0, max_side=6),
        elements=elements,
    )


@given(st.data())
def test_pandas_isna_property(data):
    # ---- Property 1: Scalar input yields scalar boolean output ----
    scalar = data.draw(scalar_strategy())
    res_scalar = pd.isna(scalar)
    assert isinstance(res_scalar, (bool, np.bool_))
    assert bool(res_scalar) == is_missing_scalar(scalar)

    # ---- Properties 2,3,4,5: numpy float array ----
    arr = data.draw(float_array_1d())
    res_arr = pd.isna(arr)
    assert isinstance(res_arr, np.ndarray)               # Property 3
    assert res_arr.dtype == np.bool_                     # Property 3
    assert res_arr.shape == arr.shape                    # Property 2
    assert np.array_equal(res_arr, np.isnan(arr))        # Property 5
    assert np.array_equal(res_arr, ~pd.notna(arr))       # Property 4

    # ---- Object array: element-wise correctness ----
    obj_arr = data.draw(object_array_1d())
    res_obj = pd.isna(obj_arr)
    assert isinstance(res_obj, np.ndarray)
    assert res_obj.dtype == np.bool_
    assert res_obj.shape == obj_arr.shape
    expected_obj = np.array([is_missing_scalar(x) for x in obj_arr], dtype=bool)
    assert np.array_equal(res_obj, expected_obj)         # Property 5
    assert np.array_equal(res_obj, ~pd.notna(obj_arr))   # Property 4

    # ---- Index input -> ndarray of bool ----
    idx = pd.Index(list(obj_arr))
    res_idx = pd.isna(idx)
    assert isinstance(res_idx, np.ndarray)               # Property 3
    assert res_idx.dtype == np.bool_
    assert res_idx.shape == (len(idx),)                  # Property 2
    assert np.array_equal(res_idx, ~pd.notna(idx))       # Property 4

    # ---- Series input -> Series of bool, index preserved ----
    ser = pd.Series(arr)
    res_ser = pd.isna(ser)
    assert isinstance(res_ser, pd.Series)                # Property 3
    assert res_ser.dtype == np.bool_
    assert res_ser.index.equals(ser.index)               # Property 2
    assert np.array_equal(res_ser.to_numpy(), np.isnan(ser.to_numpy()))  # Property 5
    assert res_ser.equals(~pd.notna(ser))                # Property 4

    # ---- DataFrame input -> DataFrame of bool ----
    arr2d = data.draw(float_array_2d())
    df = pd.DataFrame(arr2d)
    res_df = pd.isna(df)
    assert isinstance(res_df, pd.DataFrame)              # Property 3
    assert res_df.shape == df.shape                      # Property 2
    assert res_df.index.equals(df.index)                 # Property 2
    assert res_df.columns.equals(df.columns)             # Property 2
    assert (res_df.dtypes == bool).all()                 # Property 3
    assert res_df.equals(~pd.notna(df))                  # Property 4
# End program