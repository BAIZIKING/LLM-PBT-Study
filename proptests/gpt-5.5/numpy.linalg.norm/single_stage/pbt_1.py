from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate small finite float arrays with 1-4 dimensions, including zeros,
# negatives, and varied shapes. Randomly choose ord from documented vector/matrix
# norm orders plus invalid orders for some contexts, choose axis as None, an int,
# or a valid 2-tuple of axes, and vary keepdims. For valid combinations, compare
# numpy.linalg.norm against an independent implementation of the documented
# formulas and verify keepdims shape behavior. For invalid documented combinations,
# verify that ValueError is raised.
@given(st.data())
def test_numpy_linalg_norm(data):
    ndim = data.draw(st.integers(min_value=1, max_value=4))
    shape = tuple(
        data.draw(
            st.lists(
                st.integers(min_value=1, max_value=4),
                min_size=ndim,
                max_size=ndim,
            )
        )
    )

    size = int(np.prod(shape))
    value_strategy = st.one_of(
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
    values = data.draw(st.lists(value_strategy, min_size=size, max_size=size))
    x = np.array(values, dtype=float).reshape(shape)

    axis_options = [None]
    axis_options.extend(range(-ndim, ndim))
    if ndim >= 2:
        axis_options.extend(
            (i, j)
            for i in range(ndim)
            for j in range(i + 1, ndim)
        )
    axis = data.draw(st.sampled_from(axis_options))

    ord_value = data.draw(
        st.sampled_from(
            [
                None,
                np.inf,
                -np.inf,
                "fro",
                "nuc",
                0,
                1,
                -1,
                2,
                -2,
                3,
                -3,
                0.5,
                -0.5,
            ]
        )
    )
    keepdims = data.draw(st.booleans())

    def is_numeric_order(o):
        return isinstance(o, (int, float, np.integer, np.floating))

    def is_vector_order(o):
        return o is None or is_numeric_order(o)

    def is_matrix_order(o):
        return (
            o is None
            or o in ("fro", "nuc")
            or o in (np.inf, -np.inf, 1, -1, 2, -2)
        )

    def apply_keepdims(expected, normed_axes):
        if not keepdims:
            return expected

        if normed_axes is None:
            return np.asarray(expected).reshape((1,) * x.ndim)

        if isinstance(normed_axes, int):
            return np.expand_dims(expected, normed_axes % x.ndim)

        out = expected
        for ax in sorted(a % x.ndim for a in normed_axes):
            out = np.expand_dims(out, ax)
        return out

    def expected_vector_norm(arr, order, ax):
        if order is None or order == 2:
            out = np.sqrt(np.sum(np.abs(arr) ** 2, axis=ax))
        elif order == np.inf:
            out = np.max(np.abs(arr), axis=ax)
        elif order == -np.inf:
            out = np.min(np.abs(arr), axis=ax)
        elif order == 0:
            out = np.sum(arr != 0, axis=ax, dtype=float)
        else:
            with np.errstate(all="ignore"):
                out = np.sum(np.abs(arr) ** order, axis=ax) ** (1.0 / order)
        return out

    def expected_matrix_norm(arr, order, axes):
        axes = tuple(a % arr.ndim for a in axes)
        moved = np.moveaxis(arr, axes, (-2, -1))
        abs_moved = np.abs(moved)

        if order is None or order == "fro":
            out = np.sqrt(np.sum(abs_moved ** 2, axis=(-2, -1)))
        elif order == np.inf:
            out = np.max(np.sum(abs_moved, axis=-1), axis=-1)
        elif order == -np.inf:
            out = np.min(np.sum(abs_moved, axis=-1), axis=-1)
        elif order == 1:
            out = np.max(np.sum(abs_moved, axis=-2), axis=-1)
        elif order == -1:
            out = np.min(np.sum(abs_moved, axis=-2), axis=-1)
        elif order in (2, -2, "nuc"):
            singular_values = np.linalg.svd(moved, compute_uv=False)
            if order == 2:
                out = singular_values[..., 0]
            elif order == -2:
                out = singular_values[..., -1]
            else:
                out = np.sum(singular_values, axis=-1)
        else:
            raise AssertionError("invalid matrix norm order reached")
        return out

    def expected_norm():
        if axis is None:
            if ord_value is None:
                expected = np.sqrt(np.sum(np.abs(x.ravel()) ** 2))
                return True, apply_keepdims(expected, None)

            if x.ndim == 1 and is_vector_order(ord_value):
                expected = expected_vector_norm(x, ord_value, 0)
                return True, apply_keepdims(expected, None)

            if x.ndim == 2 and is_matrix_order(ord_value):
                expected = expected_matrix_norm(x, ord_value, (0, 1))
                return True, apply_keepdims(expected, None)

            return False, None

        if isinstance(axis, int):
            if not is_vector_order(ord_value):
                return False, None
            expected = expected_vector_norm(x, ord_value, axis % x.ndim)
            return True, apply_keepdims(expected, axis)

        if isinstance(axis, tuple):
            if not is_matrix_order(ord_value):
                return False, None
            expected = expected_matrix_norm(x, ord_value, axis)
            return True, apply_keepdims(expected, axis)

        return False, None

    valid, expected = expected_norm()

    try:
        with np.errstate(all="ignore"):
            result = np.linalg.norm(x, ord=ord_value, axis=axis, keepdims=keepdims)
    except ValueError:
        assert not valid
        return

    assert valid
    result = np.asarray(result)
    expected = np.asarray(expected)

    assert result.shape == expected.shape
    assert np.all(result >= -1e-12)
    np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-6)


# End program