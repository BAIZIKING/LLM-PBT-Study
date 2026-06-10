from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate scalar, vector-vector, matrix-matrix, N-D-by-vector,
# N-D-by-M-D, and intentionally incompatible inputs. Shapes include zero-length
# axes; dtypes include int, float, and complex; values are small so an explicit
# manual sum-product oracle is exact. The test checks documented shape behavior,
# scalar multiplication behavior, non-conjugating inner products, sum over the
# documented axes, ValueError for incompatible dimensions, and valid `out`
# behavior.
@given(st.data())
def test_numpy_dot(data):
    dtype = data.draw(st.sampled_from([np.int64, np.float64, np.complex128]))

    def elements_for(dt):
        ints = st.integers(-5, 5)
        if np.issubdtype(dt, np.complexfloating):
            return st.builds(complex, ints, ints)
        if np.issubdtype(dt, np.floating):
            return ints.map(float)
        return ints

    def draw_shape(rank, max_dim=4):
        return tuple(
            data.draw(
                st.lists(st.integers(0, max_dim), min_size=rank, max_size=rank)
            )
        )

    def draw_array(shape, label):
        arr = data.draw(
            hnp.arrays(dtype=dtype, shape=shape, elements=elements_for(dtype)),
            label=label,
        )
        # Sometimes pass actual Python scalars for 0-D inputs.
        if shape == () and data.draw(st.booleans(), label=f"{label}_as_python_scalar"):
            return arr.item()
        return arr

    case = data.draw(
        st.sampled_from(
            [
                "scalar",
                "vector_vector",
                "matrix_matrix",
                "nd_vector",
                "nd_md",
                "incompatible",
            ]
        )
    )

    incompatible = False

    if case == "scalar":
        other_rank = data.draw(st.integers(0, 4))
        other_shape = draw_shape(other_rank)
        scalar_on_left = data.draw(st.booleans())
        a_shape = () if scalar_on_left else other_shape
        b_shape = other_shape if scalar_on_left else ()

    elif case == "vector_vector":
        k = data.draw(st.integers(0, 5))
        a_shape = (k,)
        b_shape = (k,)

    elif case == "matrix_matrix":
        m = data.draw(st.integers(0, 4))
        k = data.draw(st.integers(0, 5))
        n = data.draw(st.integers(0, 4))
        a_shape = (m, k)
        b_shape = (k, n)

    elif case == "nd_vector":
        a_rank = data.draw(st.integers(2, 4))
        k = data.draw(st.integers(0, 5))
        a_shape = draw_shape(a_rank - 1) + (k,)
        b_shape = (k,)

    elif case == "nd_md":
        a_rank = data.draw(st.integers(1, 4))
        b_rank = data.draw(st.integers(2, 4))
        k = data.draw(st.integers(0, 5))
        last_b = data.draw(st.integers(0, 4))
        a_shape = draw_shape(a_rank - 1) + (k,)
        b_shape = draw_shape(b_rank - 2) + (k, last_b)

    else:
        incompatible = True
        a_rank = data.draw(st.integers(1, 4))
        b_rank = data.draw(st.integers(1, 4))
        k_a = data.draw(st.integers(0, 5))
        k_b = data.draw(st.integers(0, 5).filter(lambda x: x != k_a))
        a_shape = draw_shape(a_rank - 1) + (k_a,)
        if b_rank == 1:
            b_shape = (k_b,)
        else:
            last_b = data.draw(st.integers(0, 4))
            b_shape = draw_shape(b_rank - 2) + (k_b, last_b)

    a = draw_array(a_shape, "a")
    b = draw_array(b_shape, "b")
    aa = np.asarray(a)
    bb = np.asarray(b)

    if incompatible:
        try:
            np.dot(a, b)
        except ValueError:
            return
        raise AssertionError("np.dot did not raise ValueError for mismatched axes")

    result = np.dot(a, b)
    result_dtype = np.asarray(result).dtype

    def manual_dot(x, y):
        if x.ndim == 0 or y.ndim == 0:
            return np.multiply(x, y)

        if x.ndim == 1 and y.ndim == 1:
            total = np.array(0, dtype=result_dtype)
            for r in range(x.shape[0]):
                total = total + x[r] * y[r]
            return np.asarray(total, dtype=result_dtype)[()]

        if y.ndim == 1:
            out_shape = x.shape[:-1]
            out = np.empty(out_shape, dtype=result_dtype)
            for idx in np.ndindex(out_shape):
                total = np.array(0, dtype=result_dtype)
                for r in range(x.shape[-1]):
                    total = total + x[idx + (r,)] * y[r]
                out[idx] = total
            return out

        out_shape = x.shape[:-1] + y.shape[:-2] + y.shape[-1:]
        out = np.empty(out_shape, dtype=result_dtype)
        a_prefix_len = len(x.shape[:-1])
        b_prefix_len = len(y.shape[:-2])

        for idx in np.ndindex(out_shape):
            a_idx = idx[:a_prefix_len]
            rest = idx[a_prefix_len:]
            b_prefix_idx = rest[:b_prefix_len]
            b_last_idx = rest[b_prefix_len:]

            total = np.array(0, dtype=result_dtype)
            for r in range(x.shape[-1]):
                total = total + x[a_idx + (r,)] * y[b_prefix_idx + (r,) + b_last_idx]
            out[idx] = total

        return out

    expected = manual_dot(aa, bb)

    np.testing.assert_array_equal(result, expected)

    if aa.ndim == 0 or bb.ndim == 0:
        np.testing.assert_array_equal(result, np.multiply(aa, bb))
    elif aa.ndim == 1 and bb.ndim == 1:
        assert np.shape(result) == ()
    else:
        assert np.shape(result) == np.shape(expected)

    use_out = data.draw(st.booleans(), label="use_valid_out")
    if use_out and aa.ndim > 0 and bb.ndim > 0 and np.shape(result) != ():
        out = np.empty(np.shape(result), dtype=result_dtype, order="C")
        returned = np.dot(a, b, out=out)
        assert returned is out
        assert out.flags.c_contiguous
        np.testing.assert_array_equal(out, expected)
# End program