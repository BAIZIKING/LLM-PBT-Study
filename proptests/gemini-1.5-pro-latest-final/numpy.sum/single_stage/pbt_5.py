from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates various array shapes, data types, and parameter combinations for numpy.sum
@given(
    data=st.data(),
    shape=st.integers(min_value=0, max_value=5).flatmap(
        lambda d: st.tuples(*[st.integers(min_value=1, max_value=5) for _ in range(d)])
    ),
    dtype=st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float16, np.float32, np.float64, bool]),
    axis=st.one_of(st.none(), st.integers(min_value=-5, max_value=4), st.tuples(st.integers(min_value=-5, max_value=4))),
    keepdims=st.booleans(),
    initial=st.floats(allow_nan=False, allow_infinity=False),
    where=st.one_of(st.none(), st.booleans().map(lambda b: b.astype(bool))),
)
def test_numpy_sum(data, shape, dtype, axis, keepdims, initial, where):
    arr = data.draw(st.arrays(dtype, shape))
    result = np.sum(arr, axis=axis, dtype=dtype, keepdims=keepdims, initial=initial, where=where)

    # Check output shape
    expected_shape = list(arr.shape)
    if axis is not None:
        if isinstance(axis, int):
            axis = (axis,)
        for ax in axis:
            if keepdims:
                expected_shape[ax] = 1
            else:
                expected_shape.pop(ax)
    assert result.shape == tuple(expected_shape)

    # Additional checks for specific cases and properties
    # ... (add more assertions based on the property checks described above)

# End program