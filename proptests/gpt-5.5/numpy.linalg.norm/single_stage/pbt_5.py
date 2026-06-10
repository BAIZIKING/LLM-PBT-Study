from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate finite float arrays with 1-4 dimensions, small but varied shapes,
# including zeros, signed values, and size-one axes. Randomly choose among valid
# vector norms, matrix norms, axis=None cases, integer axes, 2-tuple matrix axes,
# negative axis spellings, and keepdims=True/False. Check the documented formulas
# for vector and matrix norms, the documented keepdims shape/broadcast behavior,
# and non-negativity of the returned norm.
@given(st.data())
def test_numpy_linalg_norm(data):
    elements = st.one_of(
        st.just(0.0),
        st.just(-0.0),
        st.just(1.0),
        st.just(-1.0),
        st.just(100.0),
        st.just(-100.0),
        st.floats(
            min_value=-100.0,
            max_value=100.0,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        ),
    )

    vector_ords = st.sampled_from(
        [None, np.inf, -np.inf, 0, 1, -1, 2, -2, 3, -3]
    )
    matrix_ords = st.sampled_from(
        [None, "fro", "nuc", np.inf, -np.inf, 1, -1, 2, -2]
    )

    mode = data.draw(
        st.sampled_from(
            ["axis_none_vector", "axis_none_matrix", "vector_axis", "matrix_axis"]
        )
    )
    keepdims = data.draw(st.booleans())

    def axis_spelling(axis, ndim):
        return data.draw(st.sampled_from([axis, axis - ndim]))

    if mode == "axis_none_vector":
        shape = (data.draw(st.integers(min_value=1, max_value=5)),)
        x = data.draw(hnp.arrays(np.float64, shape=shape, elements=elements))
        ord_value = data.draw(vector_ords)
        axis = None

        abs_x = np.abs(x)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_value is None or ord_value == 2:
                expected = np.sqrt(np.sum(abs_x * abs_x, axis=0, keepdims=keepdims))
            elif ord_value == np.inf:
                expected = np.max(abs_x, axis=0, keepdims=keepdims)
            elif ord_value == -np.inf:
                expected = np.min(abs_x, axis=0, keepdims=keepdims)
            elif ord_value == 0:
                expected = np.sum(x != 0, axis=0, keepdims=keepdims)
            else:
                p = float(ord_value)
                expected = np.sum(abs_x**p, axis=0, keepdims=keepdims) ** (1.0 / p)

    elif mode == "axis_none_matrix":
        shape = (
            data.draw(st.integers(min_value=1, max_value=4)),
            data.draw(st.integers(min_value=1, max_value=4)),
        )
        x = data.draw(hnp.arrays(np.float64, shape=shape, elements=elements))
        ord_value = data.draw(matrix_ords)
        axis = None

        y = x
        abs_y = np.abs(y)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_value is None or ord_value == "fro":
                base = np.sqrt(np.sum(abs_y * abs_y, axis=(-2, -1)))
            elif ord_value == np.inf:
                base = np.max(np.sum(abs_y, axis=-1), axis=-1)
            elif ord_value == -np.inf:
                base = np.min(np.sum(abs_y, axis=-1), axis=-1)
            elif ord_value == 1:
                base = np.max(np.sum(abs_y, axis=-2), axis=-1)
            elif ord_value == -1:
                base = np.min(np.sum(abs_y, axis=-2), axis=-1)
            else:
                singular_values = np.linalg.svd(y, compute_uv=False)
                if ord_value == 2:
                    base = np.max(singular_values, axis=-1)
                elif ord_value == -2:
                    base = np.min(singular_values, axis=-1)
                else:
                    base = np.sum(singular_values, axis=-1)

        expected = np.reshape(base, (1, 1)) if keepdims else base

    elif mode == "vector_axis":
        ndim = data.draw(st.integers(min_value=1, max_value=4))
        shape = tuple(
            data.draw(st.lists(st.integers(min_value=1, max_value=4),
                               min_size=ndim,
                               max_size=ndim))
        )
        x = data.draw(hnp.arrays(np.float64, shape=shape, elements=elements))
        ord_value = data.draw(vector_ords)

        normalized_axis = data.draw(st.integers(min_value=0, max_value=ndim - 1))
        axis = axis_spelling(normalized_axis, ndim)

        abs_x = np.abs(x)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_value is None or ord_value == 2:
                expected = np.sqrt(
                    np.sum(abs_x * abs_x, axis=normalized_axis, keepdims=keepdims)
                )
            elif ord_value == np.inf:
                expected = np.max(abs_x, axis=normalized_axis, keepdims=keepdims)
            elif ord_value == -np.inf:
                expected = np.min(abs_x, axis=normalized_axis, keepdims=keepdims)
            elif ord_value == 0:
                expected = np.sum(x != 0, axis=normalized_axis, keepdims=keepdims)
            else:
                p = float(ord_value)
                expected = (
                    np.sum(abs_x**p, axis=normalized_axis, keepdims=keepdims)
                    ** (1.0 / p)
                )

    else:
        ndim = data.draw(st.integers(min_value=2, max_value=4))
        shape = tuple(
            data.draw(st.lists(st.integers(min_value=1, max_value=4),
                               min_size=ndim,
                               max_size=ndim))
        )
        x = data.draw(hnp.arrays(np.float64, shape=shape, elements=elements))
        ord_value = data.draw(matrix_ords)

        axis_permutation = data.draw(st.permutations(tuple(range(ndim))))
        normalized_axes = tuple(axis_permutation[:2])
        axis = tuple(axis_spelling(a, ndim) for a in normalized_axes)

        y = np.moveaxis(x, normalized_axes, (-2, -1))
        abs_y = np.abs(y)

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            if ord_value is None or ord_value == "fro":
                base = np.sqrt(np.sum(abs_y * abs_y, axis=(-2, -1)))
            elif ord_value == np.inf:
                base = np.max(np.sum(abs_y, axis=-1), axis=-1)
            elif ord_value == -np.inf:
                base = np.min(np.sum(abs_y, axis=-1), axis=-1)
            elif ord_value == 1:
                base = np.max(np.sum(abs_y, axis=-2), axis=-1)
            elif ord_value == -1:
                base = np.min(np.sum(abs_y, axis=-2), axis=-1)
            else:
                singular_values = np.linalg.svd(y, compute_uv=False)
                if ord_value == 2:
                    base = np.max(singular_values, axis=-1)
                elif ord_value == -2:
                    base = np.min(singular_values, axis=-1)
                else:
                    base = np.sum(singular_values, axis=-1)

        if keepdims:
            keep_shape = list(x.shape)
            keep_shape[normalized_axes[0]] = 1
            keep_shape[normalized_axes[1]] = 1
            expected = np.reshape(base, keep_shape)
        else:
            expected = base

    result = np.linalg.norm(x, ord=ord_value, axis=axis, keepdims=keepdims)

    assert np.asarray(result).shape == np.asarray(expected).shape
    np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-10)

    assert np.all(np.asarray(result) >= -1e-10)

    if keepdims:
        assert np.broadcast_to(result, x.shape).shape == x.shape

# End program