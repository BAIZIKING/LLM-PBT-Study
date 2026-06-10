from hypothesis import given, strategies as st
import statistics

# 1. Test output is a float
@given(st.lists(st.floats(min_value=1e-5, max_value=1e5), min_size=1, max_size=10))
def test_output_is_float(data):
    result = statistics.geometric_mean(data)
    assert isinstance(result, float)

# 2. Test output is less than or equal to the largest number
@given(st.lists(st.floats(min_value=1e-5, max_value=1e5), min_size=1, max_size=10))
def test_output_less_than_max(data):
    result = statistics.geometric_mean(data)
    assert result <= max(data)

# 3. Test no error if input is valid
@given(st.lists(st.floats(min_value=1e-5, max_value=1e5), min_size=1, max_size=10))
def test_no_error_for_valid_input(data):
    try:
        statistics.geometric_mean(data)
    except statistics.StatisticsError:
        assert False, "Exception thrown for valid input"

# 4. Test exception when negative or zero in list
@given(st.lists(st.floats(min_value=-1e5, max_value=1e5), min_size=1, max_size=10))
def test_exception_for_invalid_input(data):
    if any(x <= 0 for x in data):
        try:
            statistics.geometric_mean(data)
            assert False, "Expected exception not thrown for invalid input"
        except statistics.StatisticsError:
            pass

# 5. Test output is the same number if all numbers in list are the same
@given(st.floats(min_value=1e-5, max_value=1e5), st.integers(min_value=1, max_value=10))
def test_same_number_if_all_same(num, length):
    data = [num] * length  
    result = statistics.geometric_mean(data) 
    assert result == num