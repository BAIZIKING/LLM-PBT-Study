from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate small NumPy arrays with scalar, empty, 1D, and multidimensional shapes; bool, signed/unsigned integer, and floating dtypes; valid axes including None, negative axes, and tuples; optional dtype, keepdims, initial, where masks, and out arrays. Check documented properties: np.sum agrees with np.add.reduce, has the documented reduced/kept shape, honors explicit dtype, and returns/fills out with cast values.
@given(st.data())
def test_numpy_sum(data):
    array_dtype = data.draw(
        st.sampled_from([np.bool_, np.int8, np.uint8, np.int16, np.int64, np.float32, np.float64])
    )
    dtype = np.dtype(array_dtype)

    shape = tuple(data.draw(st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=3)))

    if np.issubdtype(dtype, np.bool_):
        elements = st.booleans()
    elif np.issubdtype(dtype, np.unsignedinteger):
        elements = st.integers(min_value=0, max_value=20)
    elif np.issubdtype(dtype, np.signedinteger):
        elements = st.integers(min_value=-20, max_value=20)
    elif dtype == np.dtype(np.float32):
        elements = st.floats(
            min_value=-20,
            max_value=20,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        )
    else:
        elements = st.floats(
            min_value=-20,
            max_value=20,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )

    a = data.draw(hnp.arrays(dtype=array_dtype, shape=shape, elements=elements))
    ndim = a.ndim

    if ndim == 0:
        axis = None
    else:
        axis = data.draw(
            st.one_of(
                st.none(),
                st.integers(min_value=-ndim, max_value=ndim - 1),
                st.lists(
                    st.integers(min_value=0, max_value=ndim - 1),
                    min_size=1,
                    max_size=ndim,
                    unique=True,
                ).map(tuple),
            )
        )

    sum_dtype = data.draw(st.sampled_from([None, np.int8, np.int64, np.float32, np.float64]))
    keepdims = data.draw(st.booleans())

    kwargs = {"axis": axis, "keepdims": keepdims}
    if sum_dtype is not None:
        kwargs["dtype"] = sum_dtype

    if data.draw(st.booleans()):
        acc_dtype = np.dtype(sum_dtype) if sum_dtype is not None else a.dtype
        if np.issubdtype(acc_dtype, np.unsignedinteger):
            initial = data.draw(st.integers(min_value=0, max_value=10))
        elif np.issubdtype(acc_dtype, np.floating):
            initial = data.draw(
                st.one_of(
                    st.integers(min_value=-10, max_value=10),
                    st.floats(
                        min_value=-10,
                        max_value=10,
                        allow_nan=False,
                        allow_infinity=False,
                    ),
                )
            )
        else:
            initial = data.draw(st.integers(min_value=-10, max_value=10))
        kwargs["initial"] = initial

    if data.draw(st.booleans()):
        kwargs["where"] = data.draw(hnp.arrays(dtype=np.bool_, shape=shape))

    result = np.sum(a, **kwargs)
    expected = np.add.reduce(a, **kwargs)

    np.testing.assert_allclose(result, expected, rtol=1e-6, atol=1e-6)

    if axis is None:
        reduced_axes = set(range(ndim))
    elif isinstance(axis, tuple):
        reduced_axes = {ax % ndim for ax in axis}
    else:
        reduced_axes = {axis % ndim}

    if keepdims:
        expected_shape = tuple(1 if i in reduced_axes else shape[i] for i in range(ndim))
    else:
        expected_shape = tuple(shape[i] for i in range(ndim) if i not in reduced_axes)

    assert np.shape(result) == expected_shape

    if sum_dtype is not None:
        assert np.asarray(result).dtype == np.dtype(sum_dtype)

    if data.draw(st.booleans()):
        out_dtype = data.draw(st.sampled_from([np.int64, np.float32, np.float64]))
        out = np.empty(expected_shape, dtype=out_dtype)

        out_result = np.sum(a, out=out, **kwargs)

        assert out_result is out
        np.testing.assert_allclose(
            out,
            np.asarray(result, dtype=out_dtype),
            rtol=1e-6,
            atol=1e-6,
        )
# End program