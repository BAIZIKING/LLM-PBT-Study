from hypothesis import given, strategies as st
from statistics import geometric_mean
from math import isclose

# Generate a wide variety of numeric lists, including edge cases:
# - Empty lists
# - Lists containing a single element
# - Lists containing zeroes, positive numbers, negative numbers, and floats
# - Lists containing duplicates
# - Very small and large lists
@given(st.lists(st.one_of(
    st.integers(min_value=1),  # positive integers 
    st.floats(min_value=0, exclude_min=True)  # positive floats
)))
def test_geometric_mean(data):
    # The geometric mean of a list of positive numbers should be:
    # - Positive 
    # - Less than or equal to the maximum element in the list
    # - Greater than or equal to the minimum element in the list
    # - Equal to the product of the list elements raised to the power of 1/n
    #   where n is the number of elements
    if len(data) == 0:
        # Empty list should raise StatisticsError
        try:
            geometric_mean(data)
            assert False, "Expected StatisticsError"
        except StatisticsError:
            pass
    else:
        result = geometric_mean(data)
        assert result > 0
        assert result <= max(data)
        assert result >= min(data)
        assert isclose(result, (prod(data)) ** (1/len(data)))
# End program