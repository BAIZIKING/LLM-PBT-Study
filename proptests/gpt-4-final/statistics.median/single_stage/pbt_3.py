from hypothesis import given, strategies as st

from statistics import median

@given(st.lists(st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_median(nums):
    sorted_nums = sorted(nums)
    n = len(sorted_nums)
    if n % 2 == 0:
        expected_median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
    else:
        expected_median = sorted_nums[n//2]
    assert median(nums) == expected_median
# End program