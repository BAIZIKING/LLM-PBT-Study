from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate scalars and array-likes (numpy arrays, lists, Series,
# DataFrame, Index) whose elements mix ordinary values with missing-value
# markers (np.nan, None, pd.NaT, pd.NA), then verify isna is the elementwise
# logical inverse of notna and that the result is boolean-typed.
@given(st.data())
def test_pandas_isna(data):
    # Base element strategy: ordinary values plus missing markers
    missing_markers = st.sampled_from([np.nan, None, pd.NaT, pd.NA, float("nan")])
    ordinary = st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(allow_nan=False, allow_infinity=True, width=32),
        st.booleans(),
        st.text(max_size=5),
    )
    element = st.one_of(missing_markers, ordinary)

    # Choose between a scalar input or an array-like input
    kind = data.draw(st.sampled_from(["scalar", "ndarray", "list", "series", "index"]))

    if kind == "scalar":
        obj = data.draw(element)
    elif kind == "ndarray":
        elems = data.draw(st.lists(st.one_of(missing_markers,
                                             st.floats(allow_nan=False,
                                                       allow_infinity=False)),
                                   min_size=0, max_size=10))
        obj = np.array(elems, dtype=object)
    elif kind == "list":
        obj = data.draw(st.lists(element, min_size=0, max_size=10))
    elif kind == "series":
        elems = data.draw(st.lists(element, min_size=0, max_size=10))
        obj = pd.Series(elems, dtype=object)
    else:  # index
        elems = data.draw(st.lists(element, min_size=0, max_size=10))
        obj = pd.Index(elems, dtype=object)

    result = pd.isna(obj)
    inverse = pd.notna(obj)

    if np.isscalar(obj) or obj is None or kind == "scalar":
        # Property 1: scalar input -> scalar boolean
        assert isinstance(result, (bool, np.bool_))
        # Property 4: inverse relationship
        assert bool(result) == (not bool(inverse))
    else:
        # Property 2: array-like input -> array-like of booleans
        res_arr = np.asarray(result)
        inv_arr = np.asarray(inverse)
        assert res_arr.dtype == bool
        assert res_arr.shape == np.asarray(obj).shape
        # Same container type preserved for Series/Index where applicable
        if isinstance(obj, pd.Series):
            assert isinstance(result, pd.Series)
        # Property 4: elementwise inverse relationship
        assert np.array_equal(res_arr, ~inv_arr)
# End program