from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of numbers, avoiding overflows
number_strategy = st.floats(allow_nan=False, allow_infinity=False)
list_strategy = st.lists(number_strategy, min_size=1) 

@given(list_strategy)
def test_mean_order_invariance(data):
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    assert statistics.mean(data) == statistics.mean(shuffled_data)

@given(list_strategy)
def test_mean_summation_relationship(data):
    assert sum(data) == len(data) * statistics.mean(data)

@given(list_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_mean_scaling(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.mean(scaled_data) == statistics.mean(data) * factor

@given(list_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_mean_shifting(data, offset):
    shifted_data = [x + offset for x in data]
    assert statistics.mean(shifted_data) == statistics.mean(data) + offset

@given(st.lists(number_strategy, max_size=0))
def test_mean_empty_list(data):
    with pytest.raises(StatisticsError):
        statistics.mean(data)
# End program