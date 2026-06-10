from hypothesis import given, strategies as st
import numpy as np

# Summary: Pick one of dot's documented "modes" (scalar, 1D·1D, 2D·2D, ND·1D,
# ND·MD), generate shapes sharing a common contraction dimension k so that the
# last axis of a matches the contraction axis of b, fill arrays with bounded
# finite floats, then verify dot against a tensordot-based reference, check the
# scalar/inner-product special cases, the expected output shape, and the `out`
# parameter semantics.
@given(st.data())
def test_numpy_dot(data):
    elems = st.floats(min_value=-100, max_value=100, allow_nan=False,
                      allow_infinity=False, width=64)
    dim = st.integers(min_value=1, max_value=4)

    def make(shape):
        arr = data.draw(st.lists(elems, min_size=int(np.prod(shape, dtype=int)),
                                 max_size=int(np.prod(shape, dtype=int))))
        return np.array(arr, dtype=np.float64).reshape(shape)

    mode = data.draw(st.sampled_from(
        ["scalar", "1d_1d", "2d_2d", "nd_1d", "nd_md"]))

    if mode == "scalar":
        a = np.float64(data.draw(elems))
        b = make((data.draw(dim),)) if data.draw(st.booleans()) else np.float64(data.draw(elems))
        result = np.dot(a, b)
        assert np.allclose(result, a * b)
        return

    k = data.draw(dim)  # shared contraction size

    if mode == "1d_1d":
        a = make((k,))
        b = make((k,))
        result = np.dot(a, b)
        assert np.ndim(result) == 0
        assert np.allclose(result, np.sum(a * b))

    elif mode == "2d_2d":
        m = data.draw(dim)
        n = data.draw(dim)
        a = make((m, k))
        b = make((k, n))
        result = np.dot(a, b)
        ref = np.tensordot(a, b, axes=([1], [0]))
        assert result.shape == (m, n)
        assert np.allclose(result, ref)

    elif mode == "nd_1d":
        lead = data.draw(st.lists(dim, min_size=1, max_size=3))
        a = make((*lead, k))
        b = make((k,))
        result = np.dot(a, b)
        ref = np.tensordot(a, b, axes=([a.ndim - 1], [0]))
        assert result.shape == tuple(lead)
        assert np.allclose(result, ref)

    else:  # nd_md, M >= 2
        a_lead = data.draw(st.lists(dim, min_size=1, max_size=2))
        b_lead = data.draw(st.lists(dim, min_size=0, max_size=2))
        last = data.draw(dim)
        a = make((*a_lead, k))
        b = make((*b_lead, k, last))
        result = np.dot(a, b)
        # reference: contract last axis of a with second-to-last axis of b
        ref = np.tensordot(a, b, axes=([a.ndim - 1], [b.ndim - 2]))
        expected_shape = tuple(a_lead) + tuple(b_lead) + (last,)
        assert result.shape == expected_shape
        assert np.allclose(result, ref)

        # `out` parameter: must be C-contiguous, correct dtype/shape, same object
        out = np.empty(expected_shape, dtype=result.dtype)
        returned = np.dot(a, b, out=out)
        assert returned is out
        assert np.allclose(returned, result)
# End program