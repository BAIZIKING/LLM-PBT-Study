from hypothesis import given, strategies as st, assume, settings
import hypothesis.extra.numpy as hnp
import pandas as pd
import numpy as np
import math


# Strategy for scalar values that may or may not be "missing"
scalar_values = st.one_of(
    st.integers(min_value=-10**9, max_value=10**9),
    st.floats(allow_nan=True, allow_infinity=True, width=64),
    st.text(max_size=20),
    st.booleans(),
    st.none(),
    st.just(np.nan),
    st.just(pd.NA),
    st.just(pd.NaT),
)


# Strategy for numpy arrays (numeric and object)
numeric_arrays = hnp.arrays(
    dtype=st.sampled_from([np.float64, np.int64]),
    shape=hnp.array_shapes(min_dims=1, max_dims=3, max_side=10),
    elements=st.floats(allow_nan=True, allow_infinity=True, width=64),
    fill=st.nothing(),
)

object_arrays = hnp.arrays(
    dtype=object,
    shape=hnp.array_shapes(min_dims=1, max_dims=2, max_side=10),
    elements=st.one_of(
        st.text(max_size=10),
        st.none(),
        st.integers(min_value=-1000, max_value=1000),
        st.just(np.nan),
    ),
)


array_like = st.one_of(numeric_arrays, object_arrays)


def is_missing_scalar(x):
    """Reference implementation for whether a scalar is missing."""
    if x is None:
        return True
    if x is pd.NA:
        return True
    if x is pd.NaT:
        return True
    try:
        if isinstance(x, float) and math.isnan(x):
            return True
    except (TypeError, ValueError):
        pass
    try:
        if isinstance(x, (np.floating,)) and np.isnan(x):
            return True
    except (TypeError, ValueError):
        pass
    return False


@given(st.data())
def test_pandas_isna_scalar_returns_scalar_bool(data):
    """Property 1: Scalar input yields a scalar boolean output."""
    val = data.draw(scalar_values)
    result = pd.isna(val)
    # Result should not be an array-like
    assert np.isscalar(result) or isinstance(result, (bool, np.bool_))
    assert not hasattr(result, "__len__")
    assert isinstance(result, (bool, np.bool_))
# End program


@given(st.data())
def test_pandas_isna_array_shape_preserved(data):
    """Property 2: Output shape/type matches input for array-like."""
    arr = data.draw(array_like)
    result = pd.isna(arr)
    assert isinstance(result, np.ndarray)
    assert result.shape == arr.shape
    assert result.dtype == np.bool_
# End program


@given(st.data())
def test_pandas_isna_dataframe_type_preserved(data):
    """Property 2 (cont.): Series/DataFrame return same type with same index/columns."""
    arr = data.draw(object_arrays)
    df = pd.DataFrame(arr)
    result = pd.isna(df)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == df.shape
    assert list(result.index) == list(df.index)
    assert list(result.columns) == list(df.columns)
    assert (result.dtypes == bool).all()
# End program


@given(st.data())
def test_pandas_isna_correct_scalar_identification(data):
    """Property 3: Correctly identifies missing scalar values."""
    val = data.draw(scalar_values)
    result = pd.isna(val)
    expected = is_missing_scalar(val)
    assert bool(result) == expected
# End program


@given(st.data())
def test_pandas_isna_inverse_of_notna(data):
    """Property 4: pd.isna is the element-wise negation of pd.notna."""
    obj = data.draw(st.one_of(scalar_values, array_like))
    isna_res = pd.isna(obj)
    notna_res = pd.notna(obj)
    if isinstance(isna_res, np.ndarray):
        assert np.array_equal(isna_res, ~notna_res)
    else:
        assert bool(isna_res) == (not bool(notna_res))
# End program


@given(st.data())
def test_pandas_isna_output_all_boolean(data):
    """Property 5: Every element of the output is strictly boolean."""
    obj = data.draw(st.one_of(scalar_values, array_like))
    result = pd.isna(obj)
    if isinstance(result, np.ndarray):
        assert result.dtype == np.bool_
        for v in result.flatten():
            assert isinstance(v, (bool, np.bool_))
            assert v in (True, False)
    else:
        assert isinstance(result, (bool, np.bool_))
        assert result in (True, False)
# End program