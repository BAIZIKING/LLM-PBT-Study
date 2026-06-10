from hypothesis import given, strategies as st
import statistics

# Strategy for generating lists of real numbers within reasonable bounds
number_strategy = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)

@given(st.lists(number_strategy, min_size=2))
def test_variance_non_negative(data):
    """Variance should always be non-negative."""
    result = statistics.variance(data)
    assert result >= 0

@given(st.lists(number_strategy, min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_shift_invariance(data, shift_value):
    """Adding a constant to each data point should not change the variance."""
    shifted_data = [x + shift_value for x in data]
    original_variance = statistics.variance(data)
    shifted_variance = statistics.variance(shifted_data)
    assert original_variance == shifted_variance

@given(st.lists(number_strategy, min_size=2), st.floats(min_value=0.1, max_value=10, allow_nan=False, allow_infinity=False)) 
def test_variance_scale_dependence(data, scale_factor):
    """Scaling data by a factor should scale the variance by the square of that factor."""
    scaled_data = [x * scale_factor for x in data]
    original_variance = statistics.variance(data)
    scaled_variance = statistics.variance(scaled_data)
    assert scaled_variance == original_variance * scale_factor**2

@given(st.lists(number_strategy, min_size=2))
def test_variance_with_mean(data):
    """Providing the true mean should result in an unbiased variance estimate."""
    true_mean = statistics.mean(data)
    sample_variance = statistics.variance(data)
    population_variance = statistics.pvariance(data, mu=true_mean)
    # Due to floating-point limitations, we check for approximate equality
    assert abs(sample_variance - population_variance) < 1e-10

# End program