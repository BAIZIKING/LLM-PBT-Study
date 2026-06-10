from hypothesis import given, strategies as st
from statistics import correlation
from math import isclose

# Summary: Generate lists of floats with equal length between 2 and 100 elements.
# Optionally generate NaN or Inf values. Check that the correlation is between 
# -1 and 1 inclusive. Check that the correlation of a list with itself is 1.
# Check that reversing one of the lists negates the correlation. Check that
# the ranked correlation is 1 for monotonically increasing values.
@given(st.data())
def test_statistics_correlation(data):
    elements = st.floats(allow_nan=True, allow_infinity=True)
    x = data.draw(st.lists(elements, min_size=2, max_size=100))
    y = data.draw(st.lists(elements, min_size=len(x), max_size=len(x)))
    
    r = correlation(x, y)
    assert -1 <= r <= 1
    
    r_self = correlation(x, x)
    assert isclose(r_self, 1, rel_tol=1e-9)
    
    r_rev = correlation(x, list(reversed(y)))
    assert isclose(r_rev, -r, rel_tol=1e-9)
    
    x_ranks = list(range(len(x)))
    r_ranked = correlation(x_ranks, x_ranks, method='ranked')
    assert r_ranked == 1
# End program