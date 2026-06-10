from hypothesis import given, assume, strategies as st
from statistics import geometric_mean
from math import sqrt, isclose

# Summary: Generates non-empty lists of positive non-zero floats, checks that geometric mean is 
# equal to the square root of the product of those numbers. Also includes edge cases of very small 
# and large positive numbers.
@given(st.lists(st.floats(min_value=1e-10, max_value=1e10), min_size=1))
def test_geometric_mean(lst):
    assume(all(x > 0 for x in lst))  # Ensuring all values generated are positive non-zero
    
    product = 1
    for val in lst:
        product *= val

    gm = geometric_mean(lst)
    
    assert isclose(gm, pow(product, (1.0/len(lst))), rel_tol=1e-09)  # Asserting geometric mean equals to the nth root of the product
# End program