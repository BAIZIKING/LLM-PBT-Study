from hypothesis import given, strategies as st
from statistics import geometric_mean, mean

@given(st.lists(st.floats(min_value=0.1, max_value=100.0, exclude_max=True), min_size=1))
def test_statistics_geometric_mean(lst):
    # Geometric mean should always return a valid float number
    assert isinstance(geometric_mean(lst), float)
    
    # Geometric mean cannot be smaller than the smallest number in the list
    assert geometric_mean(lst) >= min(lst)
    
    # Geometric mean cannot be larger than the largest number in the list
    assert geometric_mean(lst) <= max(lst)
    
    # Geometric mean should always be less than or equal to the arithmetic mean
    assert geometric_mean(lst) <= mean(lst)
# End program