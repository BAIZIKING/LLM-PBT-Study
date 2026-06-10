from hypothesis import given, strategies as st
import statistics

# Test the output's type
@given(st.lists(st.integers()), st.lists(st.fractions()), st.lists(st.decimals()))
def test_mean_type(int_list, fractions_list, decimal_list):
    assert isinstance(statistics.mean(int_list), (int, float))
    assert isinstance(statistics.mean(fractions_list), float)
    assert isinstance(statistics.mean(decimal_list), float)

# Test the output is within min and max of a list
@given(st.lists(st.floats(min_value=0, max_value=100), min_size=1))
def test_mean_min_max(float_list):
    mean_value = statistics.mean(float_list)
    assert min(float_list) <= mean_value <= max(float_list)

# Test that mean of equal values is that value
@given(st.tuples(st.integers(), st.integers(min_size=1)))
def test_mean_of_equal_values(t):
    value, size = t
    data = [value] * size
    assert statistics.mean(data) == value

# Test that mean is independent of the order of the data
@given(st.lists(st.integers(), min_size=1))
def test_mean_order_invariance(int_list):
    assert statistics.mean(int_list) == statistics.mean(reversed(int_list))

# Test that mean is affected by adding/multiplying a constant
@given(st.lists(st.integers(), min_size=1), st.integers(), st.integers())
def test_mean_with_constant(int_list, c_add, c_mul):
    add_list = [x + c_add for x in int_list]
    mul_list = [x * c_mul for x in int_list]
    assert statistics.mean(add_list) == statistics.mean(int_list) + c_add
    assert statistics.mean(mul_list) == statistics.mean(int_list) * c_mul