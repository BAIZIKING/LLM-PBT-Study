from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of numeric data
number_strategy = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.decimals(allow_nan=False, allow_infinity=False),
    st.fractions()
)
data_strategy = st.lists(number_strategy, min_size=1)  # Ensure non-empty lists

@given(data_strategy)
def test_mean_within_range(data):
    # Property 1: Mean is within min/max range
    mean_value = statistics.mean(data)
    assert min(data) <= mean_value <= max(data)

@given(st.lists(number_strategy, min_size=1, unique=True))
def test_mean_equals_single_value(data):
    # Property 2: Mean equals single value if all elements are the same
    single_value = data[0]
    data = [single_value] * len(data)  # Make all elements the same
    mean_value = statistics.mean(data)
    assert mean_value == single_value

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_mean_scaling(data, factor):
    # Property 3: Scaling data scales the mean
    scaled_data = [x * factor for x in data]
    mean_value = statistics.mean(data)
    scaled_mean = statistics.mean(scaled_data)
    assert scaled_mean == mean_value * factor

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_mean_offset(data, offset):
    # Property 4: Adding constant offsets the mean
    offset_data = [x + offset for x in data]
    mean_value = statistics.mean(data)
    offset_mean = statistics.mean(offset_data)
    assert offset_mean == mean_value + offset

@given(data_strategy)
def test_mean_data_type(data):
    # Property 5: Mean has the same type as the data elements
    mean_value = statistics.mean(data)
    assert type(mean_value) == type(data[0]) 
# End program