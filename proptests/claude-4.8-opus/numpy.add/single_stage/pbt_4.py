from hypothesis import given, strategies as st
import numpy as np
from hypothesis.extra import numpy as hnp

# Summary: Generate pairs of broadcastable arrays (floats/ints) using
# mutually_broadcastable_shapes, with element strategies covering zeros,
# negatives, and large/small finite magnitudes (excluding NaN/inf). Then
# verify commutativity, equivalence to the '+' operator, the broadcast output
# shape, correct use of the 'out' parameter, and the additive-identity property.
@given(st.data())
def test_numpy_add(data):
    # Choose a dtype
    dtype = data.draw(
        st.sampled_from([np.float64, np.int64]),
        label="dtype",
    )

    # Generate two mutually broadcastable shapes
    shapes = data.draw(
        hnp.mutually_broadcastable_shapes(num_shapes=2, max_dims=4, max_side=5),
        label="shapes",
    )
    shape1, shape2 = shapes.input_shapes
    result_shape = shapes.result_shape

    # Element strategy with edge cases, finite values only
    if np.issubdtype(dtype, np.floating):
        elements = st.floats(
            min_value=-1e10,
            max_value=1e10,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )
    else:
        elements = st.integers(min_value=-(10**9), max_value=10**9)

    x1 = data.draw(hnp.arrays(dtype=dtype, shape=shape1, elements=elements), label="x1")
    x2 = data.draw(hnp.arrays(dtype=dtype, shape=shape2, elements=elements), label="x2")

    result = np.add(x1, x2)

    # Property 1: Output shape equals the broadcast shape
    assert result.shape == result_shape

    # Property 2: Equivalence to the '+' operator
    np.testing.assert_array_equal(result, x1 + x2)

    # Property 3: Commutativity
    np.testing.assert_array_equal(np.add(x1, x2), np.add(x2, x1))

    # Property 4: 'out' parameter is used and returned
    out = np.empty(result_shape, dtype=result.dtype)
    returned = np.add(x1, x2, out=out)
    assert returned is out
    np.testing.assert_array_equal(out, result)

    # Property 5: Additive identity (x + 0 == x)
    zero = np.zeros((), dtype=dtype)
    identity = np.add(x1, zero)
    np.testing.assert_array_equal(identity, x1)
# End program