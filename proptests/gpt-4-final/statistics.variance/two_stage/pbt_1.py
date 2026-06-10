from hypothesis import given, strategies as st
import statistics

# Property 1: Output should always be a non-negative real number
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_output_non_negative(nums):
    result = statistics.variance(nums)
    assert isinstance(result, float) and result >= 0

# Property 2: Variance of a list with equal numbers should be zero
@given(st.lists(st.just(42.0), min_size=2))
def test_variance_equal_numbers(nums):
    result = statistics.variance(nums)
    assert result == 0.0

# Property 3: Providing xbar should not change variance calculation
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_with_xbar(nums):
    mean = statistics.mean(nums)
    result_with_xbar = statistics.variance(nums, mean)
    result_without_xbar = statistics.variance(nums)
    assert result_with_xbar == result_without_xbar

# Property 4: Scaling all data points scales variance by square of factor
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_variance_scaling(nums, factor):
    scaled_nums = [x * factor for x in nums]
    variance_original = statistics.variance(nums)
    variance_scaled = statistics.variance(scaled_nums)
    assert variance_scaled == variance_original * factor**2

# Property 5: Variance should be less than or equal to the average of the squared values
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_max(nums):
    squares_average = sum([x**2 for x in nums])/len(nums)
    variance_result = statistics.variance(nums)
    assert variance_result <= squares_average