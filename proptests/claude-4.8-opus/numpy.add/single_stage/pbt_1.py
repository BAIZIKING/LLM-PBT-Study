from hypothesis import given, strategies as st
import numpy as np
from hypothesis.extra import numpy as hnp

# Summary: Generate pairs of broadcastable numpy arrays with varied dtypes
# (integers and floats including NaN/inf edge cases) using mutually_broadcastable_shapes.
# Verify equivalence to '+', commutativity, broadcast output shape, the 'out'
# parameter behavior, and the 'where' masking behavior.
@given(st.data())
def test_numpy_add(data):
    # Pick a numeric dtype: integers or floats
    dtype = data.draw(
        st.sampled_from([np.int32, np.int64, np.float32, np.float64]),
        label="dtype",
    )

    # For floats, allow special edge-case values
    if np.issubdtype(dtype, np.floating):
        elements = st.floats(
            allow_nan=True, allow_infinity=True, width=32,
        )
    else:
        elements = st.integers(min_value=-1000, max_value=1000)

    # Generate two mutually broadcastable shapes
    shapes = data.draw(
        hnp.mutually_broadcastable_shapes(num_shapes=2, min_dims=0, max_dims=3),
        label="shapes",
    )
    shape1, shape2 = shapes.input_shapes
    result_shape = shapes.result_shape

    x1 = data.draw(hnp.arrays(dtype=dtype, shape=shape1, elements=elements), label="x1")
    x2 = data.draw(hnp.arrays(dtype=dtype, shape=shape2, elements=elements), label="x2")

    result = np.add(x1, x2)

    # Helper for NaN-aware equality
    def equal(a, b):
        return np.array_equal(a, b, equal_nan=True) if np.issubdtype(
            np.asarray(a).dtype, np.floating
        ) else np.array_equal(a, b)

    # Property 1: Equivalent to the '+' operator
    assert equal(result, x1 + x2)

    # Property 2: Commutativity
    assert equal(result, np.add(x2, x1))

    # Property 3: Output shape equals the broadcast shape
    assert result.shape == result_shape

    # Property 4: 'out' parameter receives the result and is returned
    out = np.empty(result_shape, dtype=result.dtype)
    returned = np.add(x1, x2, out=out)
    assert returned is out
    assert equal(out, result)

    # Property 5: 'where' parameter - False locations retain original out values
    sentinel = np.zeros(result_shape, dtype=result.dtype)
    out2 = sentinel.copy()
    where_mask = data.draw(
        hnp.arrays(dtype=bool, shape=result_shape), label="where"
    )
    np.add(x1, x2, out=out2, where=where_mask)

    expected = np.where(where_mask, result, sentinel)
    assert equal(out2, expected)
# End program