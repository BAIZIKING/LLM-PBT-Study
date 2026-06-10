from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.integers(min_value=1))
def test_pandas_cut(x, bins):
    # Test that pandas.cut does not raise an error for valid inputs
    try:
        result = pd.cut(x, bins)
    except ValueError:
        assert False, "pandas.cut raised ValueError for valid inputs"
    
    # Test that the number of elements in the output is equal to the number of elements in 'x'
    assert len(result) == len(x), "Output size doesn't match input size"

    # Test that all output values are within the range of bins
    for val in result:
        assert val.left <= val.mid <= val.right, f"Value {val.mid} not in range ({val.left}, {val.right})"