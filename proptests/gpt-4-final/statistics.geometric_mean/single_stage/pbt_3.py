from hypothesis import given, strategies as st
from statistics import geometric_mean

@given(st.lists(st.integers(min_value=1), min_size=1))
def test_geometric_mean(list_of_numbers):
    # Testing if it raises an exception when input data contains zero or negative numbers
    try:
        result = geometric_mean(list_of_numbers)
    except ValueError:
        assert False, "The function statistics.geometric_mean should not raise an exception when all input values are positive and non-zero"
    # Testing if it doesn't raise an exception when input data is valid
    zero_include = list_of_numbers + [0]
    negative_include = list_of_numbers + [-1]
    try:
        geometric_mean(zero_include)
        geometric_mean(negative_include)
    except ValueError:
        pass  # this is expected as per the API documentation 
    else:
        assert False, "The function statistics.geometric_mean should raise an exception when the input values include zero or a negative number"
# End program