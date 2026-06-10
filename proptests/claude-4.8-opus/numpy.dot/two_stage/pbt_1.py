from hypothesis import given, strategies as st, assume, settings
import numpy as np
import hypothesis.extra.numpy as hnp

# Use a moderate float dtype and bounded values to avoid overflow/NaN issues.
safe_floats = st.floats(
    min_value=-1e3,
    max_value=1e3,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

dim_sizes = st.integers(min_value=1, max_value=6)


@given(st.data())
@settings(deadline=None)
def test_numpy_dot_scalar_multiplication_equivalence(data):
    # Property 1: When either a or b is a 0-D scalar, dot equals a * b.
    scalar = data.draw(safe_floats, label="scalar")
    other_shape = data.draw(
        hnp.array_shapes(min_dims=0, max_dims=3, min_side=1, max_side=5),
        label="other_shape",
    )
    other = data.draw(
        hnp.arrays(dtype=np.float64, shape=other_shape, elements=safe_floats),
        label="other",
    )
    # scalar as a (0-D)
    a = np.array(scalar)
    result = np.dot(a, other)
    expected = np.multiply(a, other)
    assert np.allclose(result, expected, atol=1e-6, rtol=1e-6)
    # scalar as b (0-D)
    result2 = np.dot(other, a)
    expected2 = np.multiply(other, a)
    assert np.allclose(result2, expected2, atol=1e-6, rtol=1e-6)
# End program


@given(st.data())
@settings(deadline=None)
def test_numpy_dot_1d_inner_product(data):
    # Property 2: 1-D arrays -> scalar sum of element-wise products, no conjugation.
    n = data.draw(dim_sizes, label="n")
    a = data.draw(
        hnp.arrays(dtype=np.float64, shape=(n,), elements=safe_floats), label="a"
    )
    b = data.draw(
        hnp.arrays(dtype=np.float64, shape=(n,), elements=safe_floats), label="b"
    )
    result = np.dot(a, b)
    expected = np.sum(a * b)
    assert np.ndim(result) == 0
    assert np.allclose(result, expected, atol=1e-6, rtol=1e-6)
# End program


@given(st.data())
@settings(deadline=None)
def test_numpy_dot_2d_matmul_equivalence(data):
    # Property 3: 2-D arrays -> matrix product (== a @ b).
    m = data.draw(dim_sizes, label="m")
    k = data.draw(dim_sizes, label="k")
    n = data.draw(dim_sizes, label="n")
    a = data.draw(
        hnp.arrays(dtype=np.float64, shape=(m, k), elements=safe_floats), label="a"
    )
    b = data.draw(
        hnp.arrays(dtype=np.float64, shape=(k, n), elements=safe_floats), label="b"
    )
    result = np.dot(a, b)
    expected = a @ b
    assert result.shape == (m, n)
    assert np.allclose(result, expected, atol=1e-6, rtol=1e-6)
    # Check individual entries.
    for i in range(m):
        for j in range(n):
            assert np.allclose(
                result[i, j], np.sum(a[i, :] * b[:, j]), atol=1e-6, rtol=1e-6
            )
# End program


@given(st.data())
@settings(deadline=None)
def test_numpy_dot_output_shape(data):
    # Property 4: output shape = a.shape[:-1] + b.shape[:-2] + b.shape[-1:] (for M>=2),
    # and a.shape[:-1] for b being 1-D. Both 1-D / both scalar -> scalar.
    a_shape = data.draw(
        hnp.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=4),
        label="a_shape",
    )
    k = a_shape[-1]
    # Decide whether b is 1-D or M-D (M>=2).
    b_is_1d = data.draw(st.booleans(), label="b_is_1d")
    if b_is_1d:
        b_shape = (k,)
    else:
        b_extra = data.draw(
            hnp.array_shapes(min_dims=0, max_dims=2, min_side=1, max_side=4),
            label="b_extra",
        )
        last = data.draw(dim_sizes, label="last")
        # b shape: (..., k, last) so second-to-last axis is k
        b_shape = tuple(b_extra) + (k, last)
    a = data.draw(
        hnp.arrays(dtype=np.float64, shape=a_shape, elements=safe_floats), label="a"
    )
    b = data.draw(
        hnp.arrays(dtype=np.float64, shape=b_shape, elements=safe_floats), label="b"
    )
    result = np.dot(a, b)

    if b_is_1d:
        expected_shape = a_shape[:-1]
    else:
        expected_shape = a_shape[:-1] + b_shape[:-2] + b_shape[-1:]
    assert np.shape(result) == tuple(expected_shape)
# End program


@given(st.data())
@settings(deadline=None)
def test_numpy_dot_generalized_sum_product(data):
    # Property 5: dot(a,b)[i,j,k,m] = sum(a[i,j,:] * b[k,:,m]) for N-D a, M-D b (M>=2).
    # Use a of shape (i_dim, j_dim, K) and b of shape (k_dim, K, m_dim).
    i_dim = data.draw(dim_sizes, label="i_dim")
    j_dim = data.draw(dim_sizes, label="j_dim")
    K = data.draw(dim_sizes, label="K")
    k_dim = data.draw(dim_sizes, label="k_dim")
    m_dim = data.draw(dim_sizes, label="m_dim")

    a = data.draw(
        hnp.arrays(dtype=np.float64, shape=(i_dim, j_dim, K), elements=safe_floats),
        label="a",
    )
    b = data.draw(
        hnp.arrays(dtype=np.float64, shape=(k_dim, K, m_dim), elements=safe_floats),
        label="b",
    )
    result = np.dot(a, b)
    assert result.shape == (i_dim, j_dim, k_dim, m_dim)
    # Verify a few entries.
    for i in range(i_dim):
        for j in range(j_dim):
            for k in range(k_dim):
                for m in range(m_dim):
                    expected = np.sum(a[i, j, :] * b[k, :, m])
                    assert np.allclose(
                        result[i, j, k, m], expected, atol=1e-6, rtol=1e-6
                    )
# End program