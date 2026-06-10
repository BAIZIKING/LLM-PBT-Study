from hypothesis import given, strategies as st
from statistics import variance, mean

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(allow_nan=False, allow_infinity=False))
def test_statistics_variance(data, x_bar):
    variance_val = variance(data, xbar=x_bar)
    # Check if the value is greater than or equal to zero
    assert variance_val >= 0
    # Check if variance with and without xbar are same
    m = mean(data)
    variance_val_2 = variance(data, xbar=m)
    assert variance_val == variance_val_2