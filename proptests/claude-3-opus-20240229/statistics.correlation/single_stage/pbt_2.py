from hypothesis import given, strategies as st
from statistics import correlation
from math import isclose

# Summary: Generate two lists of equal length containing floats. Use
# method to specify either Pearson or Spearman correlation. Test  
# that the correlation is between -1 and 1, and that using the same  
# input twice gives a correlation of 1.0. Also test that the correlation 
# is the same regardless of input order.
@given(st.data())
def test_statistics_correlation(data):
    lst = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), 
                             min_size=2))
    method = data.draw(st.sampled_from(['linear', 'ranked']))
    
    r = correlation(lst, lst, method=method)
    assert -1 <= r <= 1
    assert isclose(r, 1.0)
    
    lst2 = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), 
                              min_size=len(lst), max_size=len(lst)))
    r1 = correlation(lst, lst2, method=method)  
    r2 = correlation(lst2, lst, method=method)
    assert isclose(r1, r2)
# End program