from hypothesis import given, strategies as st
import numpy as np

# Define a strategy for generating arrays of various shapes and dtypes
array_strategy = st.data().map(
    lambda data: data.draw(
        st.arrays(
            dtype=data.draw(st.sampled_from(np.sctypes['float'] + np.sctypes['int'])),
            shape=data.draw(st.tuples(st.integers(min_value=0, max_value=5), st.integers(min_value=0, max_value=5))),
            elements=st.floats(allow_nan=False, allow_infinity=False)
            # Restricting elements to avoid potential overflow issues
        )
    )
)


@given(array_strategy)
def test_sum_of_zeros(arr):
    zeros_arr = np.zeros_like(arr)
    assert np.sum(zeros_arr) == 0


@given(array_strategy)
def test_commutativity(arr):
    shuffled_arr = np.random.permutation(arr.flatten()).reshape(arr.shape)
    assert np.allclose(np.sum(arr), np.sum(shuffled_arr))


@given(array_strategy, st.integers(min_value=0, max_value=1))
def test_associativity(arr, axis):
    if arr.ndim > 1:
        result1 = np.sum(np.sum(arr, axis=axis), axis=axis)
        result2 = np.sum(arr, axis=axis)
        assert np.allclose(result1, result2)


@given(array_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_distributivity_with_scalar_multiplication(arr, scalar):
    assert np.allclose(np.sum(scalar * arr), scalar * np.sum(arr)) 


@given(array_strategy)
def test_relationship_with_mean(arr):
    if arr.size > 0:  # Ensure non-empty array
        assert np.allclose(np.sum(arr), np.mean(arr) * arr.size)

# End program