from hypothesis import given, strategies as st, settings, assume
import numpy as np
import hypothesis.extra.numpy as hnp

# Use a dtype with bounded values to avoid overflow.
# We use float64 and limit magnitudes, or use integers with small ranges.

# Strategy for safe finite floating point values (bounded to avoid overflow in sums)
safe_floats = st.floats(
    min_value=-1e3, max_value=1e3,
    allow_nan=False, allow_infinity=False, width=64
)

# Small dimension sizes to keep arrays manageable
small_dim = st.integers(min_value=1, max_value=5)


@given(st.data())
def test_scalar_multiplication_equivalence():
    """Property 1: When either a or b is a 0-D scalar, dot equals element-wise multiply."""
    data = st.data
    d = test_scalar_multiplication_equivalence
    # build inputs inside using data()
    # (placeholder body, real logic below)
    pass


@given(st.data())
def test_numpy_dot_scalar(data):
    # Property 1: scalar input behaves like multiply
    scalar = data.draw(safe_floats)
    # The other operand: scalar or an array
    shape = data.draw(hnp.array_shapes(min_dims=0, max_dims=3, min_side=1, max_side=4))
    other = data.draw(hnp.arrays(dtype=np.float64, shape=shape, elements=safe_floats))

    # a is scalar, b is array
    result = np.dot(scalar, other)
    expected = np.multiply(scalar, other)
    assert np.allclose(result, expected, rtol=1e-6, atol=1e-6)
    assert result.shape == expected.shape

    # b is scalar, a is array
    result2 = np.dot(other, scalar)
    expected2 = np.multiply(other, scalar)
    assert np.allclose(result2, expected2, rtol=1e-6, atol=1e-6)
    assert result2.shape == expected2.shape


@given(st.data())
def test_numpy_dot_1d_inner_product(data):
    # Property 2: 1-D inner product correctness (no conjugation)
    n = data.draw(small_dim)
    a = data.draw(hnp.arrays(dtype=np.float64, shape=(n,), elements=safe_floats))
    b = data.draw(hnp.arrays(dtype=np.float64, shape=(n,), elements=safe_floats))

    result = np.dot(a, b)
    expected = np.sum(a * b)
    # result should be a scalar (0-d)
    assert np.ndim(result) == 0
    assert np.allclose(result, expected, rtol=1e-6, atol=1e-6)


@given(st.data())
def test_numpy_dot_output_shape(data):
    # Property 3: output shape correctness for N-D and M-D inputs
    # Build a: shape (..., K), b: shape (..., K, ...) with K shared contraction dim.
    K = data.draw(small_dim)

    # a shape: prefix_a + (K,)
    prefix_a = data.draw(hnp.array_shapes(min_dims=0, max_dims=2, min_side=1, max_side=4))
    a_shape = prefix_a + (K,)
    a = data.draw(hnp.arrays(dtype=np.float64, shape=a_shape, elements=safe_floats))

    # Decide whether b is 1-D or M-D (M >= 2)
    b_is_1d = data.draw(st.booleans())
    if b_is_1d:
        b_shape = (K,)
        b = data.draw(hnp.arrays(dtype=np.float64, shape=b_shape, elements=safe_floats))
        # output shape = a.shape[:-1]
        expected_shape = a_shape[:-1]
    else:
        # b shape: prefix_b + (K, last)
        prefix_b = data.draw(hnp.array_shapes(min_dims=0, max_dims=2, min_side=1, max_side=4))
        last = data.draw(small_dim)
        b_shape = prefix_b + (K, last)
        b = data.draw(hnp.arrays(dtype=np.float64, shape=b_shape, elements=safe_floats))
        # output shape = a.shape[:-1] + b.shape[:-2] + b.shape[-1:]
        expected_shape = a_shape[:-1] + b_shape[:-2] + (b_shape[-1],)

    result = np.dot(a, b)
    assert result.shape == expected_shape


@given(st.data())
def test_numpy_dot_sum_product_definition(data):
    # Property 4: sum-product definition consistency
    # Use a: (i, K), b: (K, j) to verify dot(a,b)[i,j] = sum(a[i,:] * b[:,j])
    K = data.draw(small_dim)
    I = data.draw(small_dim)
    J = data.draw(small_dim)

    a = data.draw(hnp.arrays(dtype=np.float64, shape=(I, K), elements=safe_floats))
    b = data.draw(hnp.arrays(dtype=np.float64, shape=(K, J), elements=safe_floats))

    result = np.dot(a, b)
    for i in range(I):
        for j in range(J):
            expected = np.sum(a[i, :] * b[:, j])
            assert np.allclose(result[i, j], expected, rtol=1e-6, atol=1e-6)


@given(st.data())
def test_numpy_dot_out_parameter(data):
    # Property 5: out parameter yields identical result and is returned
    K = data.draw(small_dim)
    I = data.draw(small_dim)
    J = data.draw(small_dim)

    a = data.draw(hnp.arrays(dtype=np.float64, shape=(I, K), elements=safe_floats))
    b = data.draw(hnp.arrays(dtype=np.float64, shape=(K, J), elements=safe_floats))

    expected = np.dot(a, b)
    out = np.empty(expected.shape, dtype=expected.dtype, order='C')
    returned = np.dot(a, b, out=out)

    # out is filled and returned
    assert returned is out
    assert np.allclose(out, expected, rtol=1e-6, atol=1e-6)
    assert np.allclose(returned, expected, rtol=1e-6, atol=1e-6)
# End program