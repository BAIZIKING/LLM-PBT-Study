from hypothesis import given, strategies as st
import numpy as np
import hypothesis.extra.numpy as npst

# Summary: We dispatch over the documented behavioral branches of numpy.dot
# (scalar, 1D-1D inner product, 2D-2D matrix product, ND-1D, and general ND-MD),
# generating shape-compatible float arrays for each. For each branch we check the
# result against an independent reference computation (multiply, sum-product,
# matmul, or tensordot) and also verify the `out` parameter behavior.
@given(st.data())
def test_numpy_dot(data):
    finite_floats = lambda: st.floats(
        min_value=-1e3, max_value=1e3,
        allow_nan=False, allow_infinity=False, width=64,
    )
    dim = lambda: st.integers(min_value=1, max_value=4)

    def make(shape):
        return data.draw(npst.arrays(dtype=np.float64, shape=shape,
                                     elements=finite_floats()))

    case = data.draw(st.sampled_from(
        ["scalar", "inner", "matrix", "nd_1d", "general"]))

    if case == "scalar":
        a = data.draw(finite_floats())
        b = make(data.draw(st.sampled_from([(), (data.draw(dim()),),
                                            (data.draw(dim()), data.draw(dim()))])))
        result = np.dot(a, b)
        np.testing.assert_allclose(result, np.multiply(a, b), rtol=1e-9, atol=1e-9)

    elif case == "inner":
        n = data.draw(dim())
        a = make((n,))
        b = make((n,))
        result = np.dot(a, b)
        assert np.ndim(result) == 0  # scalar returned
        np.testing.assert_allclose(result, np.sum(a * b), rtol=1e-7, atol=1e-7)

    elif case == "matrix":
        m, n, p = data.draw(dim()), data.draw(dim()), data.draw(dim())
        a = make((m, n))
        b = make((n, p))
        result = np.dot(a, b)
        np.testing.assert_allclose(result, a @ b, rtol=1e-7, atol=1e-7)
        # out parameter must be returned and filled
        out = np.empty_like(result)
        ret = np.dot(a, b, out=out)
        assert ret is out
        np.testing.assert_allclose(out, result, rtol=1e-7, atol=1e-7)

    elif case == "nd_1d":
        # a is N-D, b is 1-D: sum product over last axis of a and b
        shape = tuple(data.draw(st.lists(dim(), min_size=2, max_size=3)))
        a = make(shape)
        b = make((shape[-1],))
        result = np.dot(a, b)
        expected = np.tensordot(a, b, axes=([a.ndim - 1], [0]))
        np.testing.assert_allclose(result, expected, rtol=1e-7, atol=1e-7)
        assert result.shape == shape[:-1]

    else:  # general: a is N-D, b is M-D (M>=2)
        # last axis of a == second-to-last axis of b
        a_shape = tuple(data.draw(st.lists(dim(), min_size=2, max_size=3)))
        k = a_shape[-1]
        b_lead = tuple(data.draw(st.lists(dim(), min_size=0, max_size=1)))
        b_tail = (data.draw(dim()),)
        b_shape = b_lead + (k,) + b_tail
        a = make(a_shape)
        b = make(b_shape)
        result = np.dot(a, b)
        # sum over last axis of a and second-to-last axis of b
        expected = np.tensordot(a, b, axes=([a.ndim - 1], [b.ndim - 2]))
        np.testing.assert_allclose(result, expected, rtol=1e-7, atol=1e-7)
# End program