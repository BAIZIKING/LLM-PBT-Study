from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of numbers within reasonable bounds
number_strategy = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
list_strategy = st.lists(number_strategy, min_size=1)

@given(list_strategy)
def test_mean_within_range(data):
    mean_value = statistics.mean(data)
    assert min(data) <= mean_value <= max(data)

@given(list_strategy, st.floats(min_value=-100, max_value=100, exclude=0.0))
def test_mean_scaling(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.mean(scaled_data) == statistics.mean(data) * factor

@given(list_strategy, st.floats(min_value=-100, max_value=100))
def test_mean_offset(data, offset):
    offset_data = [x + offset for x in data]
    assert statistics.mean(offset_data) == statistics.mean(data) + offset

@given(list_strategy, st.integers(min_value=1, max_value=len(data)))
def test_mean_partitioning(data, split_point):
    data1, data2 = data[:split_point], data[split_point:]
    weighted_mean = (len(data1) * statistics.mean(data1) + len(data2) * statistics.mean(data2)) / len(data)
    assert statistics.mean(data) == weighted_mean

@given(st.lists(st.integers(), min_size=1, unique=True))
def test_mean_symmetric_distribution(data):
    data.sort()
    assert statistics.mean(data) == statistics.median(data)
# End program