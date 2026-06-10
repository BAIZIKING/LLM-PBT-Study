from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of numbers, avoiding overflows
number_strategy = st.integers(min_value=-10**6, max_value=10**6)
list_strategy = st.lists(number_strategy, min_size=1) 

@given(list_strategy)
def test_median_sorted_property(data):
    sorted_data = sorted(data)
    middle_index = len(data) // 2
    if len(data) % 2 == 1:
        assert statistics.median(data) == sorted_data[middle_index]
    else:
        assert statistics.median(data) == (sorted_data[middle_index - 1] + sorted_data[middle_index]) / 2

@given(list_strategy)
def test_median_extreme_value_invariance(data):
    original_median = statistics.median(data)
    data.append(10**9) # Add a large value
    data.append(-10**9) # Add a small value
    new_median = statistics.median(data)
    assert abs(original_median - new_median) < 1e-6 # Allow for small numerical differences

@given(list_strategy)
def test_median_monotonicity(data):
    original_median = statistics.median(data)
    for i in range(len(data)):
        increased_data = data.copy()
        increased_data[i] += 1
        assert statistics.median(increased_data) >= original_median

@given(list_strategy.filter(lambda x: len(x) % 2 == 0)) # Only even length lists
def test_median_average_of_two_middle(data):
    sorted_data = sorted(data)
    middle_index = len(data) // 2
    assert statistics.median(data) == (sorted_data[middle_index - 1] + sorted_data[middle_index]) / 2 

@given(list_strategy)
def test_median_subset_relationship(data):
    for subset_size in range(1, len(data) + 1):
        for subset in st.itertools.combinations(data, subset_size):
            subset_median = statistics.median(subset)
            assert min(data) <= subset_median <= max(data)
# End program