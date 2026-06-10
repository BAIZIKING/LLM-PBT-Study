from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate finite real or complex arrays with 1-4 dimensions, small non-empty shapes,
# many zeros/negative values, valid combinations of ord/axis/keepdims for vector, matrix, and
# flattened default norms. Check the documented formulas, keepdims/shape behavior, non-negativity,
# finiteness, and homogeneity under non-zero scalar multiplication.
@given(st.data())
def test_numpy_linalg_norm(data):
    def draw_axis(ndim):
        a = data.draw(st.integers(min_value=0, max_value=ndim - 1))
        return data.draw(st.sampled_from([a, a - ndim]))

    def draw_matrix_axes(ndim):
        axes = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=ndim - 1),
                min_size=2,
                max_size=2,
                unique=True,
            )
        )
        return tuple(data.draw(st.sampled_from([a, a - ndim])) for a in axes)

    def vector_reference(arr, ord_value, axis, keepdims):
        abs_arr = np.abs(arr)
        with np.errstate(all="ignore"):
            if ord_value is None or ord_value == 2:
                return np.sqrt(np.sum(abs_arr * abs_arr, axis=axis, keepdims=keepdims))
            if ord_value == np.inf:
                return np.max(abs_arr, axis=axis, keepdims=keepdims)
            if ord_value == -np.inf:
                return np.min(abs_arr, axis=axis, keepdims=keepdims)
            if ord_value == 0:
                return np.sum(arr != 0, axis=axis, keepdims=keepdims)
            return np.sum(abs_arr ** ord_value, axis=axis, keepdims=keepdims) ** (
                1.0 / ord_value
            )

    def matrix_reference(arr, ord_value, axis, keepdims):
        norm_axes = tuple(a % arr.ndim for a in axis)
        moved = np.moveaxis(arr, norm_axes, (-2, -1))
        abs_moved = np.abs(moved)

        with np.errstate(all="ignore"):
            if ord_value is None or ord_value == "fro":
                result = np.sqrt(np.sum(abs_moved * abs_moved, axis=(-2, -1)))
            elif ord_value == "nuc":
                result = np.sum(np.linalg.svd(moved, compute_uv=False), axis=-1)
            elif ord_value == np.inf:
                result = np.max(np.sum(abs_moved, axis=-1), axis=-1)
            elif ord_value == -np.inf:
                result = np.min(np.sum(abs_moved, axis=-1), axis=-1)
            elif ord_value == 1:
                result = np.max(np.sum(abs_moved, axis=-2), axis=-1)
            elif ord_value == -1:
                result = np.min(np.sum(abs_moved, axis=-2), axis=-1)
            elif ord_value == 2:
                result = np.max(np.linalg.svd(moved, compute_uv=False), axis=-1)
            elif ord_value == -2:
                result = np.min(np.linalg.svd(moved, compute_uv=False), axis=-1)
            else:
                raise AssertionError(f"unexpected matrix ord: {ord_value!r}")

        if keepdims:
            for ax in sorted(norm_axes):
                result = np.expand_dims(result, axis=ax)
        return result

    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(
        data.draw(st.integers(min_value=1, max_value=4)) for _ in range(ndim)
    )
    size = int(np.prod(shape))

    scalar_strategy = st.one_of(
        st.just(0.0),
        st.floats(
            min_value=-10,
            max_value=10,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        ),
    )

    use_complex = data.draw(st.booleans())
    real_values = data.draw(st.lists(scalar_strategy, min_size=size, max_size=size))

    if use_complex:
        imag_values = data.draw(st.lists(scalar_strategy, min_size=size, max_size=size))
        x = (
            np.asarray(real_values, dtype=np.float64)
            + 1j * np.asarray(imag_values, dtype=np.float64)
        ).reshape(shape)
    else:
        x = np.asarray(real_values, dtype=np.float64).reshape(shape)

    vector_orders = [None, np.inf, -np.inf, 0, 1, -1, 2, -2, 3, -3, 0.5]
    matrix_orders = [None, "fro", "nuc", np.inf, -np.inf, 1, -1, 2, -2]

    modes = ["flat_default", "vector_axis"]
    if ndim == 1:
        modes.append("vector_axis_none")
    if ndim == 2:
        modes.append("matrix_axis_none")
    if ndim >= 2:
        modes.append("matrix_axis_tuple")

    mode = data.draw(st.sampled_from(modes))
    keepdims = data.draw(st.booleans())

    if mode == "flat_default":
        ord_value = None
        axis = None
        expected = vector_reference(x, ord_value, axis, keepdims)
    elif mode == "vector_axis_none":
        ord_value = data.draw(st.sampled_from(vector_orders))
        axis = None
        expected = vector_reference(x, ord_value, axis, keepdims)
    elif mode == "vector_axis":
        ord_value = data.draw(st.sampled_from(vector_orders))
        axis = draw_axis(ndim)
        expected = vector_reference(x, ord_value, axis, keepdims)
    elif mode == "matrix_axis_none":
        ord_value = data.draw(st.sampled_from(matrix_orders))
        axis = None
        expected = matrix_reference(x, ord_value, (0, 1), keepdims)
    else:
        ord_value = data.draw(st.sampled_from(matrix_orders))
        axis = draw_matrix_axes(ndim)
        expected = matrix_reference(x, ord_value, axis, keepdims)

    with np.errstate(all="ignore"):
        actual = np.linalg.norm(x, ord=ord_value, axis=axis, keepdims=keepdims)

    assert np.shape(actual) == np.shape(expected)
    np.testing.assert_allclose(actual, expected, rtol=1e-7, atol=1e-7)

    actual_arr = np.asarray(actual)
    assert np.all(np.isfinite(actual_arr))
    assert np.all(actual_arr >= -1e-7)

    alpha = data.draw(
        st.one_of(
            st.floats(
                min_value=-5,
                max_value=-0.25,
                allow_nan=False,
                allow_infinity=False,
                width=32,
            ),
            st.floats(
                min_value=0.25,
                max_value=5,
                allow_nan=False,
                allow_infinity=False,
                width=32,
            ),
        )
    )

    with np.errstate(all="ignore"):
        scaled = np.linalg.norm(alpha * x, ord=ord_value, axis=axis, keepdims=keepdims)

    if ord_value == 0:
        scaled_expected = actual
    else:
        scaled_expected = abs(alpha) * actual

    np.testing.assert_allclose(scaled, scaled_expected, rtol=1e-6, atol=1e-6)

# End program