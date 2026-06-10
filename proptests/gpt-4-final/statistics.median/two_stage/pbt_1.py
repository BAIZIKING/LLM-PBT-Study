from hypothesis import given, strategies as st
import statistics

# Test 1 - median should lie within range of input data
@given(st.lists(st.integers(), min_size=1))
def test_median_in_range(nums):
    median = statistics.median(nums)
    assert min(nums) <= median <= max(nums)

# Test 2 - median is equal to any number in list if all numbers are same
@given(st.lists(st.integers().map(lambda x: [x]*5), min_size=1))
def test_median_if_all_same(nums):
    median = statistics.median(nums)
    assert median == nums[0]

# Test 3 - median is middle number if count of numbers is odd
@given(st.lists(st.integers(), min_size=1).filter(lambda x: len(x) % 2 == 1))
def test_median_in_odd_list(nums):
    median = statistics.median(nums)
    assert median == sorted(nums)[len(nums) // 2]

# Test 4 - median is same as middle number if count is even and middle numbers are same
@given(st.lists(st.integers(), min_size=4).filter(lambda x: len(x) % 2 == 0 and x[len(x) // 2 - 1] == x[len(x) // 2 ]))
def test_median_in_even_list_same_middle(nums):
    median = statistics.median(nums)
    assert median == nums[len(nums) // 2]

# Test 5 - median is average of two middle numbers if count is even and middle numbers are different
@given(st.lists(st.integers(), min_size=2).filter(lambda x: len(x) % 2 == 0 and x[len(x) // 2 - 1] != x[len(x) // 2 ]))
def test_median_in_even_list_diff_middle(nums):
    median = statistics.median(nums)
    sorted_nums = sorted(nums)
    expected = (sorted_nums[len(sorted_nums) // 2 - 1] + sorted_nums[len(sorted_nums) // 2]) / 2
    assert median == expected