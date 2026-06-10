from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of real numbers
data_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)

@given(data_strategy)
def test_variance_non_negative(data):
    """Variance should always be non-negative."""
    result = statistics.variance(data)
    assert result >= 0

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_variance_units(data, multiplier):
    """Variance units should be the square of the input data units."""
    scaled_data = [x * multiplier for x in data]
    result = statistics.variance(data)
    scaled_result = statistics.variance(scaled_data)
    assert scaled_result == result * multiplier**2

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_variance_monotonicity_with_scale(data, multiplier):
    """Variance should increase with the square of the scaling factor."""
    scaled_data = [x * multiplier for x in data]
    result = statistics.variance(data)
    scaled_result = statistics.variance(scaled_data)
    # Handle the case where multiplier is 0 separately
    if multiplier == 0:
        assert scaled_result == 0
    else:
        assert scaled_result > result

@given(data_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_variance_translation_invariance(data, offset):
    """Variance should be invariant to adding a constant to all data points."""
    shifted_data = [x + offset for x in data]
    result = statistics.variance(data)
    shifted_result = statistics.variance(shifted_data)
    assert result == shifted_result

@given(data_strategy)
def test_variance_relationship_to_stdev(data):
    """The square root of the variance should equal the standard deviation."""
    result = statistics.variance(data)
    stdev = statistics.stdev(data)
    assert abs(result - stdev**2) < 1e-10  # Account for potential floating-point errors
# End program