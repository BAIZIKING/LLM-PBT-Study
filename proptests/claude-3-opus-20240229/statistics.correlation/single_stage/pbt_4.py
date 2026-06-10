from hypothesis import given, strategies as st
from statistics import correlation
from math import isclose

# The key requirements are:
# 1. Both inputs must have the same length and be at least length 2.
# 2. The result should be between -1 and 1 for Pearson correlation.
# 3. The result should be exactly 1 for a perfect monotonic increasing relationship (Spearman).
# 4. The result should be exactly -1 for a perfect monotonic decreasing relationship (Spearman).
#
# We can generate a variety of valid inputs using:
# - Hypothesis' `lists` strategy to generate equal-length lists 
# - `floats` strategy for the values in each list
# - `sampled_from` to randomly select the correlation method
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
    st.sampled_from(['linear', 'ranked'])
)
def test_correlation(xs, ys, method):
    assume(len(xs) == len(ys))
    r = correlation(xs, ys, method=method)
    assert -1 <= r <= 1
    
    if method == 'ranked':
        # Test Spearman properties
        if sorted(xs) == xs and sorted(ys) == ys:
            assert r == 1
        elif sorted(xs, reverse=True) == xs and sorted(ys, reverse=True) == ys:  
            assert r == -1
    else:
        # Test Pearson properties
        if all(isclose(x, y) for x, y in zip(xs, ys)):
            assert isclose(r, 1)
        elif all(isclose(x, -y) for x, y in zip(xs, ys)):
            assert isclose(r, -1)
# End program            