from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2))
def test_variance_is_real_and_non_negative(data):
    result = statistics.variance(data)
    assert isinstance(result, float)
    assert result >= 0

@given(st.lists(st.just(1.0)))
def test_variance_is_zero_for_identical_values(data):
    assert statistics.variance(data) == 0

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), 
       st.floats(min_value=-1, max_value=1))
def test_variance_increases_with_data_mult_by_constant(data, constant):
    original_variance = statistics.variance(data)
    new_variance = statistics.variance([i * constant for i in data])
    assert new_variance == original_variance * (constant ** 2)

@given(st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2), 
       st.floats(min_value=-1000, max_value=1000))
def test_variance_constant_when_data_adds_constant(data, constant):
    original_variance = statistics.variance(data)
    new_variance = statistics.variance([i + constant for i in data])
    assert new_variance == original_variance
# End program