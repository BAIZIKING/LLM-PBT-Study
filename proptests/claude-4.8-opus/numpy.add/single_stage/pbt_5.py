from hypothesis import given, strategies as st, settings
from hypothesis.extra import numpy as hnp
import numpy as np

# Summary: Generate pairs of broadcastable numpy arrays with varied numeric
# dtypes (ints, floats, complex) and edge-case element values (inf, nan, zeros,
# extreme magnitudes). Also occasionally test pure-scalar inputs. We verify
# equivalence with the '+' operator, commutativity, correct broadcast output
# shape, correct behavior of the 'out' argument, and scalar-output semantics.
@given(st.data())
@settings(max_examples=300)
def test_numpy_add(data):
    # Helper: NaN-aware equality for arrays
    def equal_with_nan(a, b):
        a = np.asarray(a)
        b = np.asarray(b)
        if a.shape != b.shape:
            return False
        if np.issubdtype(a.dtype, np.floating) or np.issubdtype(a.dtype, np.complexfloating):
            both_nan = np.isnan(a) & np.isnan(b)
            close = np.isclose(a, b, rtol=1e-10, atol=1e-10, equal_nan=True)
            return bool(np.all(close | both_nan))
        return bool(np.all(a == b))

    # Property 5: pure Python scalar inputs -> scalar result
    if data.draw(st.booleans(), label="use_scalars"):
        s1 = data.draw(st.one_of(
            st.integers(min_value=-1000, max_value=1000),
            st.floats(allow_nan=True, allow_infinity=True, width=32),
        ), label="scalar1")
        s2 = data.draw(st.one_of(
            st.integers(min_value=-1000, max_value=1000),
            st.floats(allow_nan=True, allow_infinity=True, width=32),
        ), label="scalar2")
        result = np.add(s1, s2)
        # Result is a scalar (0-dimensional)
        assert np.ndim(result) == 0
        # Equivalence with '+'
        assert equal_with_nan(result, s1 + s2)
        # Commutativity
        assert equal_with_nan(np.add(s1, s2), np.add(s2, s1))
        return

    # Array case: pick a dtype
    dtype = data.draw(st.sampled_from([
        np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64,
        np.float16, np.float32, np.float64,
        np.complex64, np.complex128,
    ]), label="dtype")

    # Choose element strategy appropriate to dtype
    if np.issubdtype(dtype, np.floating):
        elements = st.floats(allow_nan=True, allow_infinity=True,
                             width=8 * np.dtype(dtype).itemsize)
    elif np.issubdtype(dtype, np.complexfloating):
        comp_width = 8 * (np.dtype(dtype).itemsize // 2)
        elements = st.complex_numbers(allow_nan=True, allow_infinity=True,
                                      width=8 * np.dtype(dtype).itemsize)
    else:
        info = np.iinfo(dtype)
        elements = st.integers(min_value=int(info.min), max_value=int(info.max))

    # Generate two broadcastable shapes
    shapes = data.draw(hnp.mutually_broadcastable_shapes(num_shapes=2, max_dims=4,
                                                         max_side=5),
                       label="shapes")
    shape1, shape2 = shapes.input_shapes
    broadcast_shape = shapes.result_shape

    x1 = data.draw(hnp.arrays(dtype=dtype, shape=shape1, elements=elements), label="x1")
    x2 = data.draw(hnp.arrays(dtype=dtype, shape=shape2, elements=elements), label="x2")

    result = np.add(x1, x2)

    # Property 3: output shape equals broadcast shape
    assert result.shape == broadcast_shape

    # Property 1: equivalence with the '+' operator
    assert equal_with_nan(result, x1 + x2)

    # Property 2: commutativity
    assert equal_with_nan(np.add(x1, x2), np.add(x2, x1))

    # Property 4: 'out' parameter returns and fills the provided array
    out = np.empty(broadcast_shape, dtype=result.dtype)
    returned = np.add(x1, x2, out=out)
    assert returned is out
    assert equal_with_nan(out, result)
# End program