from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), st.floats(min_value=-1000, max_value=1000))
def test_variance_property_positive(test_list, constant):
    var = statistics.variance(test_list)
    assert var >= 0

@given(st.lists(st.just(1.0), min_size=2))
def test_variance_property_zero(test_list):
    var = statistics.variance(test_list)
    assert var == 0.0

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), st.floats(min_value=-1000, max_value=1000))
def test_variance_property_constant_addition(test_list, constant):
    var1 = statistics.variance([i+constant for i in test_list])
    var2 = statistics.variance(test_list)
    assert var1 == var2

@given(st.lists(st.floats(min_value=-1000, max_value=1000), max_size=1))
def test_variance_property_less_than_two_values(test_list):
    try:
        var = statistics.variance(test_list)
        assert False # Should not reach here
    except statistics.StatisticsError:
        assert True 

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), st.floats(min_value=-1000, max_value=1000))
def test_variance_property_scaling_of_variance(test_list, constant):
    var1 = statistics.variance([i*constant for i in test_list])
    var2 = statistics.variance(test_list)
    assert var1 == var2 * (constant**2)