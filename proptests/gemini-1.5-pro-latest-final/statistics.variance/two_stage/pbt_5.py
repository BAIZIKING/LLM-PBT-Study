from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of real numbers, avoiding overflows
data_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)

@given(data_strategy)
def test_non_negativity(data):
    # Variance should always be non-negative
    assert statistics.variance(data) >= 0

@given(data=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=2).flatmap(
        lambda x: st.tuples(st.just(x), st.just(x))))
def test_equal_values(data):
    # Variance of identical values should be zero
    data_list = data[0]
    assert statistics.variance(data_list) == 0

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_shift_invariance(data, shift_value):
    # Shifting all values should not change the variance
    shifted_data = [x + shift_value for x in data]
    assert statistics.variance(data) == statistics.variance(shifted_data)

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False, exclude_min=True))
def test_scaling(data, scaling_factor):
    # Scaling all values should scale the variance by the square of the factor
    scaled_data = [x * scaling_factor for x in data]
    assert statistics.variance(scaled_data) == statistics.variance(data) * scaling_factor**2 

@given(data_strategy)
def test_relationship_with_pvariance(data):
    # If xbar is the true mean, variance and pvariance should be equal
    true_mean = statistics.mean(data)
    assert statistics.variance(data, true_mean) == statistics.pvariance(data, mu=true_mean)
# End program