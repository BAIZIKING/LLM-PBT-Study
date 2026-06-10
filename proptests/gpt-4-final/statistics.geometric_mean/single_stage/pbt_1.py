from hypothesis import given, strategies as st
from statistics import geometric_mean, StatisticsError
from functools import reduce
from operator import mul
from math import pow

@given(st.lists(st.floats(min_value=0.0001, max_value=10**5), min_size=1))
def test_geometric_mean(lst):
    try:
        assert round(geometric_mean(lst), 5) == round(pow(reduce(mul, lst, 1), 1/len(lst)), 5)
    except StatisticsError:
        assert len(lst) == 0 or 0 in lst or min(lst) < 0   