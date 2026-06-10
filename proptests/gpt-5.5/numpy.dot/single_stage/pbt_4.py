from hypothesis import given, strategies as st
import numpy as np

# Summary: Draws int, float, and complex NumPy arrays across scalar, vector, matrix,
# higher-dimensional, empty-axis, compatible, and deliberately incompatible shape
# cases. Valid cases check the documented dot-product formulas, result shapes, lack
# of complex conjugation, scalar multiplication behavior, matrix multiplication
# behavior, and `out` behavior for array outputs. Invalid cases check that shape
# mismatches raise ValueError.
@given(st.data())
def test_numpy_dot(data):
    dtype = data.draw(st.sampled_from([np.int64, np.float64, np.complex128]))

    def element_strategy(dtype):
        if np.issubdtype(dtype, np.integer):
            return st.integers(-5, 5)
        if np.issubdtype(dtype, np.floating):
            return st.floats(
                min_value=-10,
                max_value=10,
                allow_nan=False,
                allow_infinity=False,
                width=32,
            )
        float_part = st.floats(
            min_value=-10,
            max_value=10,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        )
        return st.builds(complex, float_part, float_part)

    def random_shape(ndim):
        return tuple(
            data.draw(
                st.lists(
                    st.integers(0, 4),
                    min_size=ndim,
                    max_size=ndim,
                )
            )
        )

    def draw_array(shape, dtype):
        size = int(np.prod(shape, dtype=int)) if shape else 1
        values = data.draw(
            st.lists(
                element_strategy(dtype),
                min_size=size,
                max_size=size,
            )
        )
        return np.asarray(values, dtype=dtype).reshape(shape)

    case = data.draw(
        st.sampled_from(
            [
                "both_scalars",
                "scalar_left",
                "scalar_right",
                "vector_vector",
                "matrix_matrix",
                "nd_by_vector",
                "nd_by_md",
                "incompatible",
            ]
        )
    )

    if case == "incompatible":
        a_ndim = data.draw(st.integers(1, 4))
        b_ndim = data.draw(st.integers(1, 4))

        shared_a_axis = data.draw(st.integers(0, 4))
        mismatched_b_axis = data.draw(
            st.sampled_from([x for x in range(5) if x != shared_a_axis])
        )

        a_shape = random_shape(a_ndim - 1) + (shared_a_axis,)

        if b_ndim == 1:
            b_shape = (mismatched_b_axis,)
        else:
            b_shape = (
                random_shape(b_ndim - 2)
                + (mismatched_b_axis,)
                + random_shape(1)
            )

        a = draw_array(a_shape, dtype)
        b = draw_array(b_shape, dtype)

        try:
            np.dot(a, b)
        except ValueError:
            return
        raise AssertionError(
            f"np.dot should raise ValueError for incompatible shapes "
            f"{a_shape} and {b_shape}"
        )

    if case == "both_scalars":
        a_shape = ()
        b_shape = ()

    elif case == "scalar_left":
        a_shape = ()
        b_shape = random_shape(data.draw(st.integers(0, 4)))

    elif case == "scalar_right":
        a_shape = random_shape(data.draw(st.integers(0, 4)))
        b_shape = ()

    elif case == "vector_vector":
        n = data.draw(st.integers(0, 4))
        a_shape = (n,)
        b_shape = (n,)

    elif case == "matrix_matrix":
        m = data.draw(st.integers(0, 4))
        n = data.draw(st.integers(0, 4))
        p = data.draw(st.integers(0, 4))
        a_shape = (m, n)
        b_shape = (n, p)

    elif case == "nd_by_vector":
        a_ndim = data.draw(st.integers(1, 4))
        n = data.draw(st.integers(0, 4))
        a_shape = random_shape(a_ndim - 1) + (n,)
        b_shape = (n,)

    else:  # "nd_by_md"
        a_ndim = data.draw(st.integers(1, 4))
        b_ndim = data.draw(st.integers(2, 4))
        n = data.draw(st.integers(0, 4))
        a_shape = random_shape(a_ndim - 1) + (n,)
        b_shape = random_shape(b_ndim - 2) + (n,) + random_shape(1)

    a = draw_array(a_shape, dtype)
    b = draw_array(b_shape, dtype)

    result = np.dot(a, b)

    if a.ndim == 0 or b.ndim == 0:
        expected = np.multiply(a, b)
        expected_shape = np.shape(expected)

    elif b.ndim == 1:
        expected = np.tensordot(a, b, axes=([-1], [0]))
        expected_shape = a.shape[:-1]

    else:
        expected = np.tensordot(a, b, axes=([-1], [-2]))
        expected_shape = a.shape[:-1] + b.shape[:-2] + b.shape[-1:]

    assert np.shape(result) == expected_shape
    np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-10)

    if a.ndim == 2 and b.ndim == 2:
        np.testing.assert_allclose(result, a @ b, rtol=1e-10, atol=1e-10)

    if np.ndim(result) > 0:
        out = np.empty(np.shape(result), dtype=np.asarray(result).dtype, order="C")
        returned = np.dot(a, b, out=out)

        assert returned is out
        assert out.flags.c_contiguous
        np.testing.assert_allclose(out, expected, rtol=1e-10, atol=1e-10)
# End program