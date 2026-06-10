from hypothesis import given, strategies as st
from statistics import correlation 
import pytest

# Summary: Test the correlation function with various list lengths and element types
@given(st.data())
def test_statistics_correlation(data):
    length = data.draw(st.integers(min_value=2))
    
    empty_list = []
    with pytest.raises(StatisticsError):
        correlation(empty_list, empty_list)
        
    integer_list1 = data.draw(st.lists(st.integers(), min_size=length, max_size=length))
    integer_list2 = data.draw(st.lists(st.integers(), min_size=length, max_size=length))
    assert -1 <= correlation(integer_list1, integer_list2) <= 1

    float_list1 = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=length, max_size=length))
    float_list2 = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=length, max_size=length))
    assert -1 <= correlation(float_list1, float_list2) <= 1

    with pytest.raises(ValueError):
        correlation(integer_list1, float_list2)
    
    assert -1 <= correlation(integer_list1, integer_list2, method='ranked') <= 1
    assert -1 <= correlation(float_list1, float_list2, method='ranked') <= 1
# End program