from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.numpy import arrays, array_shapes, integer_dtypes, floating_dtypes
import numpy as np

# Summary:
# Generate arrays of varied dtypes (signed/unsigned ints and floats), shapes
# (including 0-d and empty), and values (finite floats to keep equality stable).
# Then pick a valid axis (None, int, negative int, or tuple of ints), a keepdims
# flag, and an initial value. Check: scalar-via-None equals reduce-then-total,
# empty -> 0, keepdims shape invariants, axis-removal shape, and initial offset.
@settings(max_examples=300)
@given(st.data())
def test_numpy_sum(data):
    dtype = data.draw(st.one_of(
        integer_dtypes(endianness="="),
        floating_dtypes(endianness="=", sizes=(32, 64)),
    ))
    shape = data.draw(array_shapes(min_dims=0, max_dims=4, min_side=0, max_side=4))

    if np.issubdtype(dtype, np.floating):
        elements = st.floats(min_value=-1e6, max_value=1e6,
                             allow_nan=False, allow_infinity=False, width=32)
    else:
        elements = None  # let hypothesis pick valid integers for the dtype

    a = data.draw(arrays(dtype=dtype, shape=shape, elements=elements))
    ndim = a.ndim

    # ---- Property: empty array sums to the neutral element 0 ----
    if a.size == 0:
        assert np.sum(a) == 0
        return

    # Use float64 accumulation to avoid integer overflow / float32 precision noise
    # confusing the structural property checks.
    is_float = np.issubdtype(dtype, np.floating)
    rtol = 1e-3 if dtype == np.float32 else 1e-7

    def close(x, y):
        if is_float:
            return np.allclose(x, y, rtol=rtol, atol=1e-3, equal_nan=False)
        return np.array_equal(x, y)

    # ---- Property: axis=None returns a 0-d scalar ----
    total = np.sum(a, dtype=np.float64)
    assert np.ndim(total) == 0

    # Choose a valid axis specification.
    if ndim == 0:
        axis = None
    else:
        axis = data.draw(st.one_of(
            st.none(),
            st.integers(min_value=-ndim, max_value=ndim - 1),
            st.lists(st.integers(min_value=0, max_value=ndim - 1),
                     min_size=1, max_size=ndim, unique=True).map(tuple),
        ))

    keepdims = data.draw(st.booleans())
    res = np.sum(a, axis=axis, keepdims=keepdims, dtype=np.float64)

    # Normalize axis to a tuple of non-negative ints for shape reasoning.
    if axis is None:
        reduced = tuple(range(ndim))
    elif isinstance(axis, tuple):
        reduced = tuple(ax % ndim for ax in axis)
    else:
        reduced = (axis % ndim,)

    # ---- Property: keepdims / axis-removal shape invariants ----
    if keepdims:
        assert res.ndim == ndim
        for ax in reduced:
            assert res.shape[ax] == 1
        # result must broadcast against the input
        np.broadcast_shapes(res.shape, a.shape)
    else:
        expected_shape = tuple(s for i, s in enumerate(a.shape) if i not in reduced)
        assert res.shape == expected_shape

    # ---- Property: reduce-then-total additivity ----
    # Summing along an axis then summing the remainder equals the grand total.
    assert close(np.sum(res, dtype=np.float64), total)

    # ---- Property: initial offset ----
    k = data.draw(st.floats(min_value=-100, max_value=100,
                            allow_nan=False, allow_infinity=False))
    with_initial = np.sum(a, dtype=np.float64, initial=k)
    assert close(with_initial, total + k)
# End program