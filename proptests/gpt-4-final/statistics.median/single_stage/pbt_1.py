from hypothesis import given, strategies as st
from statistics import median, StatisticsError

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_median(nums):
    # sort for easier checking
    nums.sort()
    
    try:
        med = median(nums)
    except StatisticsError:
        # If a StatisticsError is raised, the list should be empty
        assert len(nums) == 0
    else:
        if len(nums) % 2:
            # If the number of items is odd, the median should be in the list
            assert med in nums
        else:
            # If it's even, the median should be >= the smallest and <= the largest
            assert nums[0] <= med <= nums[-1]
# End program