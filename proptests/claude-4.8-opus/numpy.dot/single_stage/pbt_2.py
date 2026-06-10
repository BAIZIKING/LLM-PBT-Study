from hypothesis import given, settings, strategies as st
import numpy as np

# Summary: Pick one of numpy.dot's documented modes (scalar*scalar, 1D inner
# product, 2D matmul, scalar*array, ND@1D, ND@MD), build compatible arrays with
# small integer/float/complex values, then verify dot against an independent
# reference (multiply / sum / tensordot), the scalar-vs-array return rule, and
# the behaviour of the `out` parameter.
@settings(max_examples=500)
@given(st.data())
def test_numpy_dot(data):
    dtype = data.draw(st.sampled_from([np.int64, np.float64, np.complex128]))

    def elems():
        if dtype == np.complex128:
            re = st.integers(-5, 5).map(float)
            im = st.integers(-5, 5).map(float)
            return st.builds(lambda r, i: complex(r, i), re, im)
        elif dtype == np.float64:
            return st.integers(-20, 20).map(float)
        else:
            return st.integers(-20, 20)

    def arr(shape):
        size = int(np.prod(shape)) if shape else 1
        vals = data.draw(st.lists(elems(), min_size=size, max_size=size))
        return np.array(vals, dtype=dtype).reshape(shape)

    dim = lambda: data.draw(st.integers(1, 4))
    case = data.draw(st.sampled_from(
        ["scalar_scalar", "1d_1d", "2d_2d", "scalar_array", "nd_1d", "nd_md"]
    ))

    if case == "scalar_scalar":
        a = arr(())[()]
        b = arr(())[()]
        result = np.dot(a, b)
        expected = a * b
        np.testing.assert_allclose(result, expected)
        assert np.ndim(result) == 0

    elif case == "1d_1d":
        n = dim()
        a = arr((n,))
        b = arr((n,))
        result = np.dot(a, b)
        expected = np.sum(a * b)  # inner product, no conjugation
        np.testing.assert_allclose(result, expected)
        assert np.ndim(result) == 0

    elif case == "2d_2d":
        i, k, j = dim(), dim(), dim()
        a = arr((i, k))
        b = arr((k, j))
        result = np.dot(a, b)
        np.testing.assert_allclose(result, a @ b)
        assert result.shape == (i, j)

    elif case == "scalar_array":
        shape = tuple(dim() for _ in range(data.draw(st.integers(1, 3))))
        b = arr(shape)
        s = arr(())[()]
        np.testing.assert_allclose(np.dot(s, b), s * b)
        np.testing.assert_allclose(np.dot(b, s), b * s)

    elif case == "nd_1d":
        ndim_a = data.draw(st.integers(2, 3))
        last = dim()
        shape_a = tuple(dim() for _ in range(ndim_a - 1)) + (last,)
        a = arr(shape_a)
        b = arr((last,))
        result = np.dot(a, b)
        expected = np.sum(a * b, axis=-1)
        np.testing.assert_allclose(result, expected)
        assert result.shape == shape_a[:-1]

    else:  # nd_md
        ndim_a = data.draw(st.integers(1, 3))
        ndim_b = data.draw(st.integers(2, 3))
        last = dim()
        shape_a = tuple(dim() for _ in range(ndim_a - 1)) + (last,)
        b_other = tuple(dim() for _ in range(ndim_b - 2))
        b_final = dim()
        shape_b = b_other + (last, b_final)
        a = arr(shape_a)
        b = arr(shape_b)
        result = np.dot(a, b)
        expected = np.tensordot(a, b, axes=([-1], [-2]))
        np.testing.assert_allclose(result, expected)

    # `out` parameter check (only meaningful when an array is returned)
    if 'a' in dir() and 'b' in dir() and case in ("2d_2d", "nd_1d", "nd_md"):
        ref = np.dot(a, b)
        out = np.empty(ref.shape, dtype=ref.dtype)
        returned = np.dot(a, b, out=out)
        assert returned is out
        np.testing.assert_allclose(out, ref)
# End program