from hypothesis import given, settings, strategies as st
import numpy as np
import hypothesis.extra.numpy as npst

# Safe float elements to avoid overflow / inf / nan during arithmetic.
safe_floats = st.floats(
    min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False, width=64
)


def float_arrays(shape):
    return npst.arrays(dtype=np.float64, shape=shape, elements=safe_floats)


# -------------------------------------------------------------------------
# Property 1: Scalar multiplication equivalence.
# If either a or b is a scalar (0-D), np.dot(a, b) == a * b.
# -------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_dot_scalar_multiplication():
    data = st.data()
    s = data.draw(safe_floats)
    shape = data.draw(npst.array_shapes(min_dims=0, max_dims=3, max_side=4))
    arr = data.draw(float_arrays(shape))

    res_left = np.dot(s, arr)
    assert np.allclose(res_left, s * arr, rtol=1e-6, atol=1e-6)

    res_right = np.dot(arr, s)
    assert np.allclose(res_right, arr * s, rtol=1e-6, atol=1e-6)
# End program


# -------------------------------------------------------------------------
# Property 2: Output shape correctness.
# For N-D a and M-D b (M>=2), output shape == a.shape[:-1] + b.shape[:-2] + b.shape[-1:].
# For two 1-D arrays the result is a scalar (0-D).
# -------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_dot_output_shape():
    data = st.data()

    # Choose a contraction dimension K shared by a's last axis and b's second-to-last axis.
    K = data.draw(st.integers(min_value=1, max_value=4))

    # a: N-D array with last axis = K
    a_lead = data.draw(
        st.lists(st.integers(min_value=1, max_value=4), min_size=0, max_size=2)
    )
    a_shape = tuple(a_lead) + (K,)
    a = data.draw(float_arrays(a_shape))

    # b: M-D array (M>=2) with second-to-last axis = K
    b_lead = data.draw(
        st.lists(st.integers(min_value=1, max_value=4), min_size=0, max_size=1)
    )
    b_last = data.draw(st.integers(min_value=1, max_value=4))
    b_shape = tuple(b_lead) + (K, b_last)
    b = data.draw(float_arrays(b_shape))

    result = np.dot(a, b)
    expected_shape = a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
    assert result.shape == expected_shape

    # 1-D x 1-D yields a scalar (0-D)
    v = data.draw(float_arrays((K,)))
    w = data.draw(float_arrays((K,)))
    scalar_res = np.dot(v, w)
    assert np.ndim(scalar_res) == 0
# End program


# -------------------------------------------------------------------------
# Property 3: Inner product for 1-D arrays.
# np.dot(a, b) == sum(a[i] * b[i]) without complex conjugation.
# -------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_dot_1d_inner_product():
    data = st.data()
    n = data.draw(st.integers(min_value=0, max_value=8))
    a = data.draw(float_arrays((n,)))
    b = data.draw(float_arrays((n,)))

    result = np.dot(a, b)
    expected = np.sum(a * b)
    assert np.allclose(result, expected, rtol=1e-6, atol=1e-6)
# End program


# -------------------------------------------------------------------------
# Property 4: Sum-product definition for higher dimensions.
# dot(a, b)[..., k, ..., m] = sum(a[i,...,:] * b[k,...,:,m]).
# We verify with N-D a (last axis K) and 1-D b (length K):
# sum product over the last axis of a.
# -------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_dot_nd_with_1d_sum_product():
    data = st.data()
    K = data.draw(st.integers(min_value=1, max_value=4))
    a_lead = data.draw(
        st.lists(st.integers(min_value=1, max_value=4), min_size=1, max_size=2)
    )
    a_shape = tuple(a_lead) + (K,)
    a = data.draw(float_arrays(a_shape))
    b = data.draw(float_arrays((K,)))

    result = np.dot(a, b)
    # Expected: sum product over the last axis of a with b.
    expected = np.sum(a * b, axis=-1)
    assert result.shape == expected.shape
    assert np.allclose(result, expected, rtol=1e-6, atol=1e-6)
# End program


# -------------------------------------------------------------------------
# Property 5: Equivalence with the `out` parameter.
# np.dot(a, b, out=out) matches np.dot(a, b) and returns the same object as out.
# -------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_numpy_dot_out_parameter():
    data = st.data()
    K = data.draw(st.integers(min_value=1, max_value=4))
    m = data.draw(st.integers(min_value=1, max_value=4))
    p = data.draw(st.integers(min_value=1, max_value=4))

    # 2-D matrix multiplication: (m, K) @ (K, p) -> (m, p)
    a = data.draw(float_arrays((m, K)))
    b = data.draw(float_arrays((K, p)))

    expected = np.dot(a, b)
    out = np.empty(expected.shape, dtype=expected.dtype)
    returned = np.dot(a, b, out=out)

    # out is modified in place and returned
    assert returned is out
    assert np.allclose(out, expected, rtol=1e-6, atol=1e-6)
# End program