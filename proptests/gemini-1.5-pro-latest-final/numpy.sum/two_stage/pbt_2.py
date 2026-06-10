from hypothesis import given, strategies as st
import numpy as np

# Define strategies for generating input data
array_strategy = st.arrays(dtype=np.float64, shape=st.tuples(st.integers(1, 5), st.integers(1, 5)), elements=st.floats(allow_nan=False, allow_infinity=False))
axis_strategy = st.one_of(st.none(), st.integers(min_value=-2, max_value=1), st.tuples(st.integers(min_value=-2, max_value=1), st.integers(min_value=-2, max_value=1)))
dtype_strategy = st.sampled_from([np.int32, np.float32, np.float64])
keepdims_strategy = st.booleans()
initial_strategy = st.floats(allow_nan=False, allow_infinity=False)


@given(data=st.data())
def test_numpy_sum_dtype(data):
    arr = data.draw(array_strategy)
    dtype = data.draw(dtype_strategy)
    result = np.sum(arr, dtype=dtype)
    assert result.dtype == dtype


@given(data=st.data())
def test_numpy_sum_shape(data):
    arr = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    result = np.sum(arr, axis=axis)
    expected_shape = tuple(s for i, s in enumerate(arr.shape) if i != axis) if isinstance(axis, int) else arr.shape  # Adjust shape based on axis
    assert result.shape == expected_shape


@given(data=st.data())
def test_numpy_sum_value(data):
    arr = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    result = np.sum(arr, axis=axis)
    expected_result = np.add.reduce(arr, axis=axis)  # Use alternative summation for comparison
    np.testing.assert_allclose(result, expected_result)


@given(data=st.data())
def test_numpy_sum_keepdims(data):
    arr = data.draw(array_strategy)
    axis = data.draw(axis_strategy)
    keepdims = data.draw(keepdims_strategy)
    result = np.sum(arr, axis=axis, keepdims=keepdims)
    expected_shape = tuple(s if i != axis else 1 for i, s in enumerate(arr.shape)) if isinstance(axis, int) else arr.shape  # Adjust shape based on axis and keepdims
    assert result.shape == expected_shape


@given(data=st.data())
def test_numpy_sum_initial(data):
    arr = data.draw(array_strategy)
    initial = data.draw(initial_strategy)
    result = np.sum(arr, initial=initial)
    expected_result = np.add.reduce(arr) + initial  # Add initial value to the expected sum
    np.testing.assert_allclose(result, expected_result)

# End program