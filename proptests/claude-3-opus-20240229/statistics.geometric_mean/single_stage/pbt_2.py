from hypothesis import given, strategies as st
from statistics import geometric_mean
from math import isclose
import numpy as np

# Generate a variety of valid inputs:
# - Lists of floats/ints > 0 (the typical case) 
# - A list containing just a single float/int > 0
# - Very large and very small positive numbers
# Also generate some invalid edge cases:
# - Empty list 
# - List containing a 0
# - List containing a negative number
@given(st.one_of(
    st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=1),
    st.lists(st.integers(min_value=1), min_size=1),
    st.lists(st.floats(min_value=1e-100, max_value=1e100), min_size=0, max_size=0),
    st.lists(st.floats(min_value=-1e100, max_value=0), min_size=1),
    st.lists(st.integers(max_value=0), min_size=1)
))
def test_geometric_mean(data):
    if len(data) == 0 or 0 in data or min(data) < 0:
        try:
            geometric_mean(data)
            assert False, "Expected StatisticsError"
        except StatisticsError:
            pass
    else:
        result = geometric_mean(data) 
        np_result = np.prod(data)**(1/len(data))
        assert isclose(result, np_result), f"Expected {np_result}, got {result}"
# End program