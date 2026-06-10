from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate small 1-D/2-D/3-D finite numeric arrays with singleton and regular dimensions,
# choose valid combinations of ord/axis/keepdims for vector norms, matrix norms, and the default
# flattened case, including edge orders such as +/-inf, 0, negative orders, Frobenius, and nuclear.
# Check independently computed norm formulas, output shape behavior, keepdims broadcasting shape,
# and non-negativity as documented.
@given(st.data())
def test_numpy_linalg_norm(data):
    ndim = data.draw(st.integers(min_value=1, max_value=3), label="ndim")
    shape = tuple(
        data.draw(st.integers(min_value=1, max_value=4), label=f"dim_{i}")
        for i in range(ndim)
    )

    size = int(np.prod(shape))
    elements = st.one_of(
        st.just(0.0),
        st.just(-0.0),
        st.floats(
            min_value=-10.0,
            max_value=10.0,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        ),
    )
    values = data.draw(
        st.lists(elements, min_size=size, max_size=size),
        label="array_values",
    )
    x = np.asarray(values, dtype=float).reshape(shape)

    possible_cases = ["default_flattened"]
    possible_cases.append("vector_axis")
    if ndim == 1:
        possible_cases.append("vector_no_axis")
    if ndim == 2:
        possible_cases.append("matrix_no_axis")
    if ndim >= 2:
        possible_cases.append("matrix_axis")

    case = data.draw(st.sampled_from(possible_cases), label="case")
    keepdims = data.draw(st.booleans(), label="keepdims")

    vector_ords = [None, np.inf, -np.inf, 0, 1, -1, 2, -2, 3, -3, 0.5]
    matrix_ords = [None, "fro", "nuc", np.inf, -np.inf, 1, -1, 2, -2]

    def maybe_negative_axis(axis, ndim):
        if data.draw(st.booleans(), label=f"use_negative_axis_{axis}"):
            return axis - ndim
        return axis

    if case == "default_flattened":
        axis = None
        ord_ = None
        norm_kind = "flat_vector"

    elif case == "vector_no_axis":
        axis = None
        ord_ = data.draw(st.sampled_from(vector_ords), label="vector_ord")
        norm_kind = "vector"

    elif case == "vector_axis":
        ax = data.draw(st.integers(min_value=0, max_value=ndim - 1), label="vector_axis")
        axis = maybe_negative_axis(ax, ndim)
        ord_ = data.draw(st.sampled_from(vector_ords), label="vector_ord")
        norm_kind = "vector"

    elif case == "matrix_no_axis":
        axis = None
        ord_ = data.draw(st.sampled_from(matrix_ords), label="matrix_ord")
        norm_kind = "matrix"
        matrix_axes = (0, 1)

    else:
        ax1 = data.draw(st.integers(min_value=0, max_value=ndim - 1), label="matrix_axis_1")
        ax2 = data.draw(
            st.integers(min_value=0, max_value=ndim - 1).filter(lambda a: a != ax1),
            label="matrix_axis_2",
        )
        axis = (maybe_negative_axis(ax1, ndim), maybe_negative_axis(ax2, ndim))
        ord_ = data.draw(st.sampled_from(matrix_ords), label="matrix_ord")
        norm_kind = "matrix"
        matrix_axes = (ax1, ax2)

    def vector_expected(abs_x, ord_, axis, keepdims):
        if ord_ is None or ord_ == 2:
            return np.sqrt(np.sum(abs_x * abs_x, axis=axis, keepdims=keepdims))
        if ord_ == np.inf:
            return np.max(abs_x, axis=axis, keepdims=keepdims)
        if ord_ == -np.inf:
            return np.min(abs_x, axis=axis, keepdims=keepdims)
        if ord_ == 0:
            return np.sum(x != 0, axis=axis, keepdims=keepdims)
        return np.sum(abs_x ** ord_, axis=axis, keepdims=keepdims) ** (1.0 / ord_)

    def matrix_expected(abs_x, ord_, axes, keepdims):
        moved = np.moveaxis(abs_x, axes, (-2, -1))

        if ord_ is None or ord_ == "fro":
            result = np.sqrt(np.sum(moved * moved, axis=(-2, -1)))
        elif ord_ == np.inf:
            result = np.max(np.sum(moved, axis=-1), axis=-1)
        elif ord_ == -np.inf:
            result = np.min(np.sum(moved, axis=-1), axis=-1)
        elif ord_ == 1:
            result = np.max(np.sum(moved, axis=-2), axis=-1)
        elif ord_ == -1:
            result = np.min(np.sum(moved, axis=-2), axis=-1)
        else:
            singular_values = np.linalg.svd(moved, compute_uv=False)
            if ord_ == "nuc":
                result = np.sum(singular_values, axis=-1)
            elif ord_ == 2:
                result = np.max(singular_values, axis=-1)
            elif ord_ == -2:
                result = np.min(singular_values, axis=-1)
            else:
                raise AssertionError(f"unexpected matrix ord: {ord_!r}")

        if keepdims:
            result = np.asarray(result)
            axes_set = set(axes)
            result_shape = []
            batch_dim = 0
            for i in range(ndim):
                if i in axes_set:
                    result_shape.append(1)
                else:
                    result_shape.append(result.shape[batch_dim])
                    batch_dim += 1
            result = result.reshape(result_shape)

        return result

    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        got = np.linalg.norm(x, ord=ord_, axis=axis, keepdims=keepdims)
        abs_x = np.abs(x)

        if norm_kind == "flat_vector":
            expected = vector_expected(abs_x, None, None, keepdims)
        elif norm_kind == "vector":
            expected = vector_expected(abs_x, ord_, axis, keepdims)
        else:
            expected = matrix_expected(abs_x, ord_, matrix_axes, keepdims)

    got_arr = np.asarray(got)
    expected_arr = np.asarray(expected)

    assert got_arr.shape == expected_arr.shape
    assert np.allclose(got_arr, expected_arr, rtol=1e-5, atol=1e-6, equal_nan=True)
    assert np.all(got_arr >= -1e-6)
# End program