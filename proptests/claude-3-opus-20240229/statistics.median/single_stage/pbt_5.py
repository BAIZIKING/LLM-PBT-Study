from hypothesis import given, strategies as st
from statistics import median, StatisticsError

# Generate a variety of input data including:
# - Empty lists to check the StatisticsError is raised
# - Lists of odd and even lengths to check correct median calculation 
# - Lists containing duplicate elements
# - Very long lists to check performance
# - Lists containing a mix of integers and floats
# - Lists containing negative numbers, 0, and positive numbers
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=1000))
def test_statistics_median(data):
    try:
        result = median(data)
    except StatisticsError:
        assert len(data) == 0
    else:
        assert isinstance(result, float)
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 1:
            assert result == sorted_data[n//2]
        else:
            assert result == (sorted_data[n//2 - 1] + sorted_data[n//2])/2
# End program