from hypothesis import given, strategies as st, assume
import hypothesis.extra.numpy as npst
import hypothesis.extra.pandas as pdst
import numpy as np
import pandas
import math


# A strategy for scalar values that may or may not be "missing".
missing_scalars = st.sampled_from([np.nan, None, pandas.NA, pandas.NaT])
non_missing_scalars = st.one_of(
    st.integers(min_value=-(10**9), max_value=10**9),
    st.floats(allow_nan=False, allow_infinity=False,
              min_value=-1e15, max_value=1e15),
    st.text(min_size=0, max_size=20),
    st.booleans(),
)
any_scalar = st.one_of(missing_scalars, non_missing_scalars)


# Strategy for 1-D numpy float arrays (which can hold NaN).
def float_arrays():
    return npst.arrays(
        dtype=np.float64,
        shape=npst.array_shapes(min_dims=1, max_dims=2, min_side=0, max_side=10),
        elements=st.one_of(
            st.floats(allow_nan=True, allow_infinity=False,
                      min_value=-1e15, max_value=1e15),
            st.just(np.nan),
        ),
    )


# Strategy for object arrays which may contain None / nan / strings / numbers.
def object_arrays():
    return npst.arrays(
        dtype=object,
        shape=npst.array_shapes(min_dims=1, max_dims=1, min_side=0, max_side=10),
        elements=any_scalar,
    )


def array_strategy():
    return st.one_of(float_arrays(), object_arrays())


def series_strategy():
    return st.builds(
        pandas.Series,
        st.lists(any_scalar, min_size=0, max_size=10),
    )


def dataframe_strategy():
    return pdst.data_frames(
        columns=[
            pdst.column("a", elements=any_scalar, dtype=object),
            pdst.column("b", elements=any_scalar, dtype=object),
        ],
        index=pdst.range_indexes(min_size=0, max_size=10),
    )


# --------------------------------------------------------------------------
# Property 1: Inverse relationship with notna.
# --------------------------------------------------------------------------
@given(st.data())
def test_pandas_isna_inverse_of_notna(data):
    obj = data.draw(
        st.one_of(any_scalar, array_strategy(), series_strategy(), dataframe_strategy())
    )
    isna_result = pandas.isna(obj)
    notna_result = pandas.notna(obj)

    if np.isscalar(isna_result) or isinstance(isna_result, (bool, np.bool_)):
        assert bool(isna_result) == (not bool(notna_result))
    elif isinstance(isna_result, pandas.DataFrame):
        assert (isna_result == (~notna_result)).all().all()
    elif isinstance(isna_result, pandas.Series):
        assert (isna_result == (~notna_result)).all()
    else:  # ndarray
        assert np.array_equal(isna_result, ~np.asarray(notna_result))
# End program


# --------------------------------------------------------------------------
# Property 2: Output type and shape preservation for array-like inputs.
# --------------------------------------------------------------------------
@given(st.data())
def test_pandas_isna_type_and_shape_preservation(data):
    obj = data.draw(
        st.one_of(array_strategy(), series_strategy(), dataframe_strategy())
    )
    result = pandas.isna(obj)

    if isinstance(obj, pandas.DataFrame):
        assert isinstance(result, pandas.DataFrame)
        assert result.shape == obj.shape
        assert (result.dtypes == bool).all()
    elif isinstance(obj, pandas.Series):
        assert isinstance(result, pandas.Series)
        assert result.shape == obj.shape
        assert result.dtype == bool
    else:  # ndarray
        assert isinstance(result, np.ndarray)
        assert result.shape == obj.shape
        assert result.dtype == bool
# End program


# --------------------------------------------------------------------------
# Property 3: Scalar input yields scalar boolean.
# --------------------------------------------------------------------------
@given(st.data())
def test_pandas_isna_scalar_returns_scalar_bool(data):
    obj = data.draw(any_scalar)
    result = pandas.isna(obj)
    assert isinstance(result, (bool, np.bool_))
    assert not isinstance(result, np.ndarray)
# End program


# --------------------------------------------------------------------------
# Property 4: Correct identification of known missing / non-missing values.
# --------------------------------------------------------------------------
@given(st.data())
def test_pandas_isna_correct_identification(data):
    is_missing = data.draw(st.booleans())
    if is_missing:
        obj = data.draw(missing_scalars)
        assert bool(pandas.isna(obj)) is True
    else:
        obj = data.draw(non_missing_scalars)
        # Exclude floats that happen to be NaN (none generated here, but be safe).
        if isinstance(obj, float):
            assume(not math.isnan(obj))
        assert bool(pandas.isna(obj)) is False
# End program


# --------------------------------------------------------------------------
# Property 5: Element-wise correctness/consistency with scalar isna.
# --------------------------------------------------------------------------
@given(st.data())
def test_pandas_isna_elementwise_consistency(data):
    obj = data.draw(st.one_of(array_strategy(), series_strategy()))
    result = pandas.isna(obj)

    flat_input = np.asarray(obj).ravel()
    flat_result = np.asarray(result).ravel()

    for inp_elem, res_elem in zip(flat_input, flat_result):
        assert bool(res_elem) == bool(pandas.isna(inp_elem))
# End program