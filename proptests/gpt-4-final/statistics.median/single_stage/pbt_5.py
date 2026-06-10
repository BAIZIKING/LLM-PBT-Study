from hypothesis import given, strategies as st, assume
from statistics import median, StatisticsError

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_median(list_of_values):
    # Making sure the generated list is not empty to avoid StatisticsError
    assume(list_of_values)

    # Sorting the list to find the expected median value
    sorted_values = sorted(list_of_values)
    length = len(sorted_values)
    if length % 2 == 0:
        expected_median = (sorted_values[length//2 - 1] + sorted_values[length//2]) / 2
    else:
        expected_median = sorted_values[length//2]

    assert median(list_of_values) == expected_median