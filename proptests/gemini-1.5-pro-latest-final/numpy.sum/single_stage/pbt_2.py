from hypothesis import given, strategies as st
import numpy as np

# Summary: Generates diverse arrays, axis values, and parameter combinations.
@given(
    data=st.data(),
    arr=st.arrays(
        dtype=st.sampled_from([np.int8, np.int16, np.int32, np.int64, np.float32, np.float64, bool]),
        shape=st.tuples(st.integers(0, 5), st.integers(0, 5)),
        elements=st.floats(allow_nan=True, allow_infinity=True) | st.integers() | st.booleans(),
    ),
    axis=st.one_of(st.none(), st.integers(), st.tuples(st.integers())),
    dtype=st.sampled_from([np.int32, np.int64, np.float32, np.float64]),
    keepdims=st.booleans(),
    initial=st.one_of(st.none(), st.integers(), st.floats()),
    where=st.arrays(dtype=bool, shape=st.tuples(st.integers(0, 5), st.integers(0, 5))),
)
def test_numpy_sum(data, arr, axis, dtype, keepdims, initial, where):
    # Generate random parameters within constraints
    result = np.sum(arr, axis=axis, dtype=dtype, keepdims=keepdims, initial=initial, where=where)

    # Check if result matches expected sum
    expected_sum = np.sum(np.where(where, arr, 0), axis=axis, dtype=dtype, keepdims=keepdims, initial=initial)  
    assert np.allclose(result, expected_sum)

    # Additional checks for specific cases and properties can be added here
    # ...