from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np
import warnings

# Summary: Generate small NumPy arrays with varied shapes, including scalars, 1-D, multi-D,
# empty dimensions, integer/unsigned/boolean/float dtypes, valid positive/negative axes or
# axis=None, optional accumulator dtype, and optional out arrays. Check documented properties:
# output shape/size, ndarray return type, out identity, dtype behavior when out is absent, and
# cumulative recurrence when the stored output dtype is suitable for checking it directly.
@given(st.data())
def test_numpy_cumsum(data):
    input_dtype = data.draw(
        st.sampled_from(
            [
                np.bool_,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
                np.float16,
                np.float32,
                np.float64,
            ]
        ),
        label="input_dtype",
    )

    ndim = data.draw(st.integers(min_value=0, max_value=3), label="ndim")
    shape = data.draw(
        hnp.array_shapes(min_dims=ndim, max_dims=ndim, min_side=0, max_side=5),
        label="shape",
    )

    if np.dtype(input_dtype).kind in "iu":
        elements = st.integers(
            min_value=np.iinfo(input_dtype).min,
            max_value=np.iinfo(input_dtype).max,
        )
    elif np.dtype(input_dtype).kind == "b":
        elements = st.booleans()
    else:
        elements = st.floats(
            width=32 if np.dtype(input_dtype) == np.dtype(np.float32) else 16 if np.dtype(input_dtype) == np.dtype(np.float16) else 64,
            allow_nan=True,
            allow_infinity=True,
        )

    a = data.draw(hnp.arrays(dtype=input_dtype, shape=shape, elements=elements), label="a")

    if ndim == 0:
        axis = None
    else:
        axis = data.draw(
            st.one_of(
                st.none(),
                st.integers(min_value=-ndim, max_value=ndim - 1),
            ),
            label="axis",
        )

    dtype = data.draw(
        st.one_of(
            st.none(),
            st.sampled_from(
                [
                    np.int32,
                    np.int64,
                    np.uint32,
                    np.uint64,
                    np.float32,
                    np.float64,
                ]
            ),
        ),
        label="dtype",
    )

    expected_shape = (a.size,) if axis is None else a.shape

    use_out = data.draw(st.booleans(), label="use_out")
    if use_out:
        out_dtype = data.draw(
            st.sampled_from([np.int64, np.float64, np.float32]),
            label="out_dtype",
        )
        out = np.empty(expected_shape, dtype=out_dtype)
    else:
        out = None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        result = np.cumsum(a, axis=axis, dtype=dtype, out=out)

    assert isinstance(result, np.ndarray)
    assert result.shape == expected_shape
    assert result.size == a.size

    if out is not None:
        assert result is out
    else:
        if dtype is not None:
            assert result.dtype == np.dtype(dtype)

    if axis is None:
        assert result.ndim == 1
    elif a.ndim == 1:
        assert result.shape == a.shape
    else:
        assert result.shape == a.shape

    # Check the cumulative recurrence when no differently-typed out array can obscure
    # the accumulator by casting intermediate stored values.
    if out is None and result.size > 0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)

            if axis is None:
                flat_a = a.ravel()
                assert np.allclose(
                    result[0],
                    np.asarray(flat_a[0], dtype=result.dtype),
                    equal_nan=True,
                )

                for i in range(1, result.size):
                    expected = np.asarray(
                        np.asarray(result[i - 1], dtype=result.dtype)
                        + np.asarray(flat_a[i], dtype=result.dtype),
                        dtype=result.dtype,
                    )
                    assert np.allclose(result[i], expected, equal_nan=True)

            else:
                moved_a = np.moveaxis(a, axis, 0)
                moved_result = np.moveaxis(result, axis, 0)

                if moved_result.shape[0] > 0:
                    assert np.allclose(
                        moved_result[0],
                        np.asarray(moved_a[0], dtype=result.dtype),
                        equal_nan=True,
                    )

                for i in range(1, moved_result.shape[0]):
                    expected = np.asarray(
                        np.asarray(moved_result[i - 1], dtype=result.dtype)
                        + np.asarray(moved_a[i], dtype=result.dtype),
                        dtype=result.dtype,
                    )
                    assert np.allclose(moved_result[i], expected, equal_nan=True)
# End program