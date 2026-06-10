from hypothesis import given, strategies as st
import statistics

# Define strategies for generating data
data_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)  # At least two elements
constant_strategy = st.floats(allow_nan=False, allow_infinity=False)

# Property 1: Non-negative variance
@given(data_strategy)
def test_variance_non_negative(data):
    result = statistics.variance(data)
    assert result >= 0

# Property 2: Zero variance for constant data
@given(constant_strategy, st.integers(min_value=2))
def test_variance_constant_data(constant, size):
    data = [constant] * size
    result = statistics.variance(data)
    assert result == 0

# Property 3: Variance increases with data spread
@given(data_strategy, st.floats(min_value=0.1, allow_nan=False, allow_infinity=False))
def test_variance_increases_with_spread(data, factor):
    scaled_data = [x * factor for x in data]
    original_variance = statistics.variance(data)
    scaled_variance = statistics.variance(scaled_data)
    assert scaled_variance > original_variance

# Property 4: Invariant to shift
@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_variance_invariant_to_shift(data, shift_value):
    shifted_data = [x + shift_value for x in data]
    original_variance = statistics.variance(data)
    shifted_variance = statistics.variance(shifted_data)
    assert original_variance == shifted_variance

# Property 5: Scales with data scaling
@given(data_strategy, st.floats(min_value=0.1, allow_nan=False, allow_infinity=False))
def test_variance_scales_with_scaling(data, scale_factor):
    scaled_data = [x * scale_factor for x in data]
    original_variance = statistics.variance(data)
    scaled_variance = statistics.variance(scaled_data)
    assert scaled_variance == original_variance * (scale_factor ** 2)

# End program 