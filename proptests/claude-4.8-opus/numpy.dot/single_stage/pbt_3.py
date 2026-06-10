from hypothesis import given, strategies as st
import numpy as np

# Summary: Generate inputs covering all documented dot cases — scalar (0-D),
# 1-D inner product, 2-D matmul, N-D × 1-D, and N-D × M-D — by choosing a shared
# contraction dimension k so that a.shape[-1] == b.shape[-2] (or [-1] for 1-D b).
# Verify against a reference (np.multiply for scalars, np.tensordot otherwise),
# check output shape, scalar-return rule, and the `out` parameter.
@given(st.data())
def test_numpy_dot(data):
    # finite, well-behaved element strategy
    elements = st.one_of(
        st.integers(min_value=-100, max_value=100),
        st.floats(min_value=-1e3, max_value=1e3, allow_nan=False,
                  allow_infinity=False, width=32),
    )

    def gen_array(shape):
        size = int(np.prod(shape)) if shape else 1
        vals = data.draw(st.lists(elements, min_size=size, max_size=size))
        arr = np.array(vals, dtype=float)
        return arr.reshape(shape)

    dim = st.integers(min_value=1, max_value=4)
    k = data.draw(dim)  # shared contraction dimension

    case = data.draw(st.sampled_from(
        ["scalar", "1d1d", "2d2d", "nd1d", "ndmd"]))

    if case == "scalar":
        a = data.draw(elements)
        b = gen_array(tuple(data.draw(st.lists(dim, min_size=0, max_size=3))))
        result = np.dot(a, b)
        expected = np.multiply(a, b)
        assert np.allclose(result, expected)
        assert np.shape(result) == np.shape(expected)
        return

    if case == "1d1d":
        a = gen_array((k,))
        b = gen_array((k,))
        result = np.dot(a, b)
        expected = np.sum(a * b)
        assert np.isscalar(result) or np.ndim(result) == 0
        assert np.allclose(result, expected)
        return

    if case == "2d2d":
        m = data.draw(dim)
        n = data.draw(dim)
        a = gen_array((m, k))
        b = gen_array((k, n))

    elif case == "nd1d":
        lead = tuple(data.draw(st.lists(dim, min_size=1, max_size=2)))
        a = gen_array(lead + (k,))
        b = gen_array((k,))

    else:  # ndmd: a is N-D, b is M-D (M>=2)
        lead_a = tuple(data.draw(st.lists(dim, min_size=1, max_size=2)))
        lead_b = tuple(data.draw(st.lists(dim, min_size=0, max_size=2)))
        last_b = data.draw(dim)
        a = gen_array(lead_a + (k,))
        b = gen_array(lead_b + (k, last_b))

    result = np.dot(a, b)

    # Reference: sum over last axis of a and second-to-last axis of b.
    # For 1-D b, tensordot over a's last and b's only axis.
    if b.ndim == 1:
        expected = np.tensordot(a, b, axes=([a.ndim - 1], [0]))
    else:
        expected = np.tensordot(a, b, axes=([a.ndim - 1], [b.ndim - 2]))

    # Expected shape per documentation:
    # a.shape[:-1] + b.shape[:-2] + b.shape[-1:]  (for b.ndim>=2)
    if b.ndim == 1:
        exp_shape = a.shape[:-1]
    else:
        exp_shape = a.shape[:-1] + b.shape[:-2] + b.shape[-1:]

    assert result.shape == exp_shape
    assert np.allclose(result, expected)

    # Check `out` parameter consistency.
    out = np.empty(result.shape, dtype=result.dtype)
    out = np.ascontiguousarray(out)
    returned = np.dot(a, b, out=out)
    assert returned is out
    assert np.allclose(out, result)
# End program