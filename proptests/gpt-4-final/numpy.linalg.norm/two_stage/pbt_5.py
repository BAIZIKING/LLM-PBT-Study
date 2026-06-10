from hypothesis import given, strategies as st
import numpy as np

# Property 1: Output type
@given(st.lists(st.floats()))
def test_output_type(lst):
    result = np.linalg.norm(lst)
    assert isinstance(result, (float, np.ndarray))

# Property 2: For a scalar input, output should be absolute value of the scalar
@given(st.floats())
def test_scalar_input(x):
    assert np.linalg.norm(x) == abs(x)

# Property 3: 2-norm of a 1-D array should not be negative
@given(st.lists(st.floats()))
def test_two_norm(lst):
    result = np.linalg.norm(lst, ord=2)
    assert result >= 0

# Property 4: Using same ord twice should result in same output
@given(st.lists(st.floats()), st.integers(min_value=1, max_value=10))
def test_same_ord(lst, ord):
    result1 = np.linalg.norm(lst, ord=ord)
    result2 = np.linalg.norm(lst, ord=ord)
    assert result1 == result2

# Property 5: 1-norm for vector with non-negative values should be equal to sum of its values
@given(st.lists(st.floats(min_value=0)))
def test_norm_of_non_negative_vector_equals_sum(lst):
    assert np.linalg.norm(lst, ord=1) == sum(lst)

# End program