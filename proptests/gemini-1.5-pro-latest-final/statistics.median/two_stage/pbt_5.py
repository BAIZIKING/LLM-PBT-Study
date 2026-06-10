from hypothesis import given, strategies as st
import statistics

# Property 1: Median >= Minimum Value
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))  # Avoid NaN and infinity for reliable comparisons
def test_median_greater_than_equal_to_min(data):
    if data:
        assert statistics.median(data) >= min(data)

# Property 2: Median <= Maximum Value
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_median_less_than_equal_to_max(data):
    if data:
        assert statistics.median(data) <= max(data)

# Property 3: Median Position in Sorted Data
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_median_position_in_sorted_data(data):
    if data:
        sorted_data = sorted(data)
        median = statistics.median(data)
        mid_index = len(data) // 2
        if len(data) % 2 == 1:  # Odd length
            assert median == sorted_data[mid_index]
        else:  # Even length
            assert median == (sorted_data[mid_index - 1] + sorted_data[mid_index]) / 2

# Property 4: Adding/Removing Values Outside Middle Range
@given(st.lists(st.integers()))
def test_median_unchanged_by_outside_values(data):
    if len(data) >= 2:
        original_median = statistics.median(data)
        data.append(min(data) - 1)  # Add value below minimum
        data.append(max(data) + 1)  # Add value above maximum
        assert statistics.median(data) == original_median

# Property 5: Median as Average of Middle Two for Even Length
@given(st.lists(st.integers(), min_size=2, max_size=1000))  # Limit size to avoid slow tests
def test_median_average_of_middle_two(data):
    if len(data) % 2 == 0:  # Even length
        sorted_data = sorted(data)
        mid_index = len(data) // 2
        expected_median = (sorted_data[mid_index - 1] + sorted_data[mid_index]) / 2
        assert statistics.median(data) == expected_median
# End program