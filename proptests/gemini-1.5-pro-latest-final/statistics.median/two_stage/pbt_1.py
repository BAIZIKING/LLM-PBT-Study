from hypothesis import given, strategies as st
import statistics

# Property 1: Sorted Data Independence
@given(st.lists(st.integers()))
def test_median_sort_independence(data):
    sorted_data = sorted(data)
    assert statistics.median(data) == statistics.median(sorted_data)

# Property 2: Element Removal
@given(st.lists(st.integers(), min_size=3))
def test_median_element_removal(data):
    data_length = len(data)
    median_index = data_length // 2

    if data_length % 2 == 0:
        # Remove elements outside the middle two
        for i in range(median_index - 2):
            del data[0]
            del data[-1]
    else:
        # Remove elements outside the middle one
        for i in range(median_index - 1):
            del data[0]
            del data[-1]

    assert statistics.median(data) == statistics.median(sorted(data))

# Property 3: Average of Middle Pair
@given(st.lists(st.integers(), min_size=2, max_size=1000))
def test_median_average_middle_pair(data):
    sorted_data = sorted(data)
    data_length = len(data)
    
    if data_length % 2 == 0:
        middle_index = data_length // 2
        expected_median = (sorted_data[middle_index - 1] + sorted_data[middle_index]) / 2
        assert statistics.median(data) == expected_median

# Property 4: Middle Value
@given(st.lists(st.integers(), min_size=1, max_size=1001))
def test_median_middle_value(data):
    sorted_data = sorted(data)
    data_length = len(data)

    if data_length % 2 == 1:
        middle_index = data_length // 2
        expected_median = sorted_data[middle_index]
        assert statistics.median(data) == expected_median

# Property 5: Monotonicity
@given(st.lists(st.integers(), min_size=1), st.integers())
def test_median_monotonicity(data, constant):
    shifted_data = [x + constant for x in data]
    assert statistics.median(shifted_data) == statistics.median(data) + constant 
# End program