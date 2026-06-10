from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of real numbers, avoiding overflows
number_strategy = st.floats(allow_nan=False, allow_infinity=False)
data_strategy = st.lists(number_strategy, min_size=2)

@given(data_strategy)
def test_variance_non_negative(data):
    # Variance should always be non-negative
    assert statistics.variance(data) >= 0

@given(data_strategy, st.floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_variance_scale(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.variance(scaled_data) == statistics.variance(data) * factor**2

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_variance_translation_invariance(data, offset):
    shifted_data = [x + offset for x in data]
    assert statistics.variance(shifted_data) == statistics.variance(data)

@given(data_strategy)
def test_variance_unbiased_estimator(data):
    pop_mean = statistics.mean(data)
    sample_variance = statistics.variance(data)
    pop_variance = statistics.pvariance(data, mu=pop_mean)
    # Due to randomness, we can't assert exact equality, but check if they are close
    assert abs(sample_variance - pop_variance) < 1e-10

@given(data_strategy)
def test_variance_consistency_with_mean(data):
    calculated_variance = statistics.variance(data)
    mean_value = statistics.mean(data)
    expected_variance = statistics.mean([(x - mean_value)**2 for x in data])
    assert calculated_variance == expected_variance 
# End program