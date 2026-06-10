from hypothesis import given, strategies as st
import statistics

# Test property 1.
@given(st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_output_number(numbers):
    result = statistics.mean(numbers)
    assert isinstance(result, (int, float))

# Test property 2.
@given(st.lists(st.integers(), min_size=1).filter(lambda x: all(e == x[0] for e in x)))
def test_mean_identical_numbers(numbers):
    result = statistics.mean(numbers)
    assert result == numbers[0]

# Test property 3.
@given(st.lists(st.integers(), min_size=2))
def test_mean_within_range(numbers):
    result = statistics.mean(numbers)
    assert min(numbers) <= result <= max(numbers)

# Test property 4.
@given(st.lists(st.integers(), min_size=1))
def test_mean_order_invariance(numbers):
    result = statistics.mean(numbers)
    numbers.reverse()
    assert result == statistics.mean(numbers)

# Test property 5.
@given(st.lists(st.integers(), min_size=1), st.integers())
def test_mean_shift(numbers, shift):
    shifted_numbers = [n + shift for n in numbers]
    result = statistics.mean(numbers)
    shifted_result = statistics.mean(shifted_numbers)
    assert shifted_result - result == shift
# End program