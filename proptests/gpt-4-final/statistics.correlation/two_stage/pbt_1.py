from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2), 
       st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2))
def test_statistics_correlation_property(list1, list2):
    if len(list1) != len(list2): # Ensure lists are of same lengths
        return
    # Property 1: Output is always a float
    result = statistics.correlation(list1, list2)
    assert isinstance(result, float)
    
    # Property 2: Return value is in range -1 to 1 inclusive
    assert -1 <= result <= 1
    
@given(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2))
def test_statistics_correlation_property_perfect_correlation(list1):
    # Property 3: Function returns 1.0 for identical lists
    assert statistics.correlation(list1, list1) == 1.0

@given(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2))
def test_statistics_correlation_property_reverse_correlation(list1):
    # Property 4: Function returns -1.0 for reversed lists
    list2 = list1[::-1] # reversed list
    assert statistics.correlation(list1, list2) == -1.0

@given(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2), 
       st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2))
def test_statistics_correlation_property_methods(list1, list2):
    # Property 5: Different results for methods 'linear' and 'ranked' unless data is linear
    if len(list1) != len(list2): # Ensure lists are of same lengths
        return
    result1 = statistics.correlation(list1, list2, method='linear')
    result2 = statistics.correlation(list1, list2, method='ranked')
    assert result1 != result2 or result1 == 1.0 or result1 == -1.0
# End program