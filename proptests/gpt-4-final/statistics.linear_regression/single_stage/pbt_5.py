from hypothesis import given, strategies as st
import numpy as np
import statistics

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate two lists of floating point numbers of same random length
    len_list = data.draw(st.integers(min_value=2))  # Ensure list length is greater than 1
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=len_list, max_size=len_list))
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=len_list, max_size=len_list))

    # Ensure x is not a list of constant values
    if np.std(x) == 0:  
        x = [i + 1 for i in x]

    # Test the function
    res = statistics.linear_regression(x, y)

    # Property 1: input lists are of the same length
    assert len(x) == len(y)

    # Property 3: output is a tuple of 2 float elements
    assert isinstance(res, tuple) and len(res) == 2
    assert isinstance(res[0], float) and isinstance(res[1], float)

    # Now, repeat the function execution with proportional=True
    res_proportional = statistics.linear_regression(x, y, proportional=True)

    # Property 4: when proportional=True, the second output should always be 0.0.
    assert res_proportional[1] == 0.0