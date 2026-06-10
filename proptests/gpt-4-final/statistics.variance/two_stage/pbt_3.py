from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(), min_size=2))
def test_variance_always_non_negative(data):
    result = statistics.variance(data)
    assert result >= 0

@given(st.lists(st.floats(), min_size=2))
def test_variance_zero_when_all_numbers_are_same(data):
    num = data[0]
    constant_data = [num]*len(data)
    result = statistics.variance(constant_data)
    assert result == 0

@given(st.lists(st.floats(), min_size=2))
def test_variance_non_zero_when_some_numbers_differ(data):
    if data[1] != data[0]:
        result = statistics.variance(data)
        assert result != 0

@given(st.lists(st.floats(), min_size=2))
def test_variance_invariant_to_order(data):
    result = statistics.variance(data)
    data_reversed = list(reversed(data))
    result_reversed = statistics.variance(data_reversed)
    assert result == result_reversed

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_invariant_to_constant_shift(data, shift):
    result = statistics.variance(data)
    shifted_data = [num + shift for num in data]
    result_shifted = statistics.variance(shifted_data)
    assert result == result_shifted
# End program