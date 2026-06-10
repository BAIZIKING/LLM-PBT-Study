from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_property(test_list):
    result = statistics.median(test_list)
    
    # Always a number
    assert isinstance(result, (int, float))

    # When list length is odd, output should be in the list
    if len(test_list) % 2 != 0:
        assert result in test_list

    # When list length is even, output should be the mean of two middle values
    elif len(test_list) % 2 == 0:
        sorted_list = sorted(test_list)
        middle_index = len(test_list) // 2
        expected_result = (sorted_list[middle_index - 1] + sorted_list[middle_index]) / 2
        assert result == expected_result

    # Output should be <= elements in right half and >= elements in left half of sorted list
    sorted_list = sorted(test_list)
    median_index = len(sorted_list) // 2
    assert all(x <= result for x in sorted_list[median_index:])
    assert all(x >= result for x in sorted_list[:median_index])

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=0))
def test_median_property_empty_input(test_list):
    try:
        statistics.median(test_list)
    except (statistics.StatisticsError):
        assert True
# End program