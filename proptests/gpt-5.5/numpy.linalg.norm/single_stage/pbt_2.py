from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generates small non-empty real/complex arrays with 1-4 dimensions, valid combinations of ord/axis/keepdims for vector norms, matrix norms, and the axis=None/ord=None flattening case; includes zeros, negative values, fractional/negative orders, infinities as norm orders, tuple axes, and keepdims broadcasting checks.
@given(st.data())
def test_numpy_linalg_norm(data):
    def draw_shape(ndim):
        return tuple(
            data.draw(st.integers(min_value=1, max_value=4), label=f"dim_{i}")
            for i in range(ndim)
        )

    def draw_array(shape):
        elements = st.complex_numbers(
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=False,
            width=32,
            max_magnitude=100,
        )
        return data.draw(
            hnp.arrays(dtype=np.complex128, shape=shape, elements=elements),
            label="x",
        )

    def vector_reference(a, ord_, axis, keepdims):
        abs_a = np.abs(a)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_ is None or ord_ == 2:
                return np.sqrt(np.sum(abs_a * abs_a, axis=axis, keepdims=keepdims))
            if ord_ == np.inf:
                return np.max(abs_a, axis=axis, keepdims=keepdims)
            if ord_ == -np.inf:
                return np.min(abs_a, axis=axis, keepdims=keepdims)
            if ord_ == 0:
                return np.count_nonzero(a, axis=axis, keepdims=keepdims)

            return np.sum(abs_a ** ord_, axis=axis, keepdims=keepdims) ** (1.0 / ord_)

    def matrix_reference(a, ord_, axis, keepdims):
        ndim = a.ndim

        if axis is None:
            axes_norm = (0, 1)
        else:
            axes_norm = tuple(ax % ndim for ax in axis)

        m = np.moveaxis(a, axes_norm, (-2, -1))
        abs_m = np.abs(m)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_ is None or ord_ == "fro":
                ref = np.sqrt(np.sum(abs_m * abs_m, axis=(-2, -1)))
            elif ord_ == np.inf:
                ref = np.max(np.sum(abs_m, axis=-1), axis=-1)
            elif ord_ == -np.inf:
                ref = np.min(np.sum(abs_m, axis=-1), axis=-1)
            elif ord_ == 1:
                ref = np.max(np.sum(abs_m, axis=-2), axis=-1)
            elif ord_ == -1:
                ref = np.min(np.sum(abs_m, axis=-2), axis=-1)
            else:
                singular_values = np.linalg.svd(m, compute_uv=False)
                if ord_ == "nuc":
                    ref = np.sum(singular_values, axis=-1)
                elif ord_ == 2:
                    ref = singular_values[..., 0]
                elif ord_ == -2:
                    ref = singular_values[..., -1]
                else:
                    raise AssertionError(f"unexpected matrix ord: {ord_!r}")

        if keepdims:
            for ax in sorted(axes_norm):
                ref = np.expand_dims(ref, axis=ax)

        return ref

    case = data.draw(
        st.sampled_from(["default_flattened_norm", "vector_norm", "matrix_norm"]),
        label="case",
    )
    keepdims = data.draw(st.booleans(), label="keepdims")

    if case == "default_flattened_norm":
        ndim = data.draw(st.integers(min_value=1, max_value=4), label="ndim")
        shape = draw_shape(ndim)
        x = draw_array(shape)
        ord_ = None
        axis = None
        expected = vector_reference(x, ord_, axis, keepdims)

    elif case == "vector_norm":
        ndim = data.draw(st.integers(min_value=1, max_value=4), label="ndim")
        shape = draw_shape(ndim)
        x = draw_array(shape)

        normalized_axis = data.draw(
            st.integers(min_value=0, max_value=ndim - 1),
            label="vector_axis",
        )
        axis = data.draw(
            st.sampled_from([normalized_axis, normalized_axis - ndim]),
            label="possibly_negative_vector_axis",
        )

        ord_ = data.draw(
            st.sampled_from(
                [None, np.inf, -np.inf, 0, 1, -1, 2, -2, 3, -3, 0.5, -0.5]
            ),
            label="vector_ord",
        )
        expected = vector_reference(x, ord_, axis, keepdims)

    else:
        ndim = data.draw(st.integers(min_value=2, max_value=4), label="ndim")
        shape = draw_shape(ndim)
        x = draw_array(shape)

        if ndim == 2:
            axis = data.draw(st.sampled_from([None, (0, 1), (1, 0), (-2, -1)]))
        else:
            normalized_axes = data.draw(
                st.lists(
                    st.integers(min_value=0, max_value=ndim - 1),
                    min_size=2,
                    max_size=2,
                    unique=True,
                ),
                label="matrix_axes",
            )
            axis = tuple(
                data.draw(st.sampled_from([ax, ax - ndim]), label=f"matrix_axis_{i}")
                for i, ax in enumerate(normalized_axes)
            )

        ord_ = data.draw(
            st.sampled_from([None, "fro", "nuc", np.inf, -np.inf, 1, -1, 2, -2]),
            label="matrix_ord",
        )
        expected = matrix_reference(x, ord_, axis, keepdims)

    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        actual = np.linalg.norm(x, ord=ord_, axis=axis, keepdims=keepdims)

    assert np.shape(actual) == np.shape(expected)
    assert np.allclose(actual, expected, rtol=1e-9, atol=1e-9, equal_nan=True)

    actual_array = np.asarray(actual)
    assert np.all(actual_array >= -1e-9)

    if keepdims:
        assert np.broadcast_to(actual, x.shape).shape == x.shape
# End program