from hypothesis import given, strategies as st
import numpy as np
from hypothesis.extra import numpy as hnp

# Summary: Generate two broadcastable arrays sharing one dtype (integer or float,
# including special float values like nan/inf), then verify np.add equals the +
# operator, is commutative, produces the broadcast shape, and respects `out`.
@given(st.data())
def test_numpy_add(data):
    # Pick a shared dtype: integers (wraparound) or floats (special values).
    dtype = data.draw(
        st.one_of(
            hnp.integer_dtypes(),
            hnp.unsigned_integer_dtypes(),
            hnp.floating_dtypes(),
        ),
        label="dtype",
    )

    # Two mutually broadcastable shapes (covers scalars, mismatch, empty).
    shapes = data.draw(
        hnp.mutually_broadcastable_shapes(num_shapes=2),
        label="shapes",
    )
    shape1, shape2 = shapes.input_shapes
    result_shape = shapes.result_shape

    # Element strategy: allow special float values when applicable.
    if np.issubdtype(dtype, np.floating):
        elements = st.floats(
            allow_nan=True, allow_infinity=True, width=np.dtype(dtype).itemsize * 8
        )
    else:
        elements = None  # use default integer elements for the dtype

    x1 = data.draw(hnp.arrays(dtype=dtype, shape=shape1, elements=elements), label="x1")
    x2 = data.draw(hnp.arrays(dtype=dtype, shape=shape2, elements=elements), label="x2")

    # Helper: element-wise equality treating NaN positions as equal.
    def nan_equal(a, b):
        a = np.asarray(a)
        b = np.asarray(b)
        if a.shape != b.shape:
            return False
        if np.issubdtype(a.dtype, np.floating):
            nan_a = np.isnan(a)
            nan_b = np.isnan(b)
            return bool(np.array_equal(nan_a, nan_b)) and bool(
                np.all(a[~nan_a] == b[~nan_b])
            )
        return bool(np.array_equal(a, b))

    result = np.add(x1, x2)

    # Property 1: output shape equals the broadcast shape.
    assert result.shape == result_shape

    # Property 2: equivalent to the + operator.
    assert nan_equal(result, x1 + x2)

    # Property 3: commutativity.
    assert nan_equal(result, np.add(x2, x1))

    # Property 4: `out` parameter receives the result and is returned.
    out = np.empty(result_shape, dtype=result.dtype)
    returned = np.add(x1, x2, out=out)
    assert returned is out
    assert nan_equal(out, result)
# End program