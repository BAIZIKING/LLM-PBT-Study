from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_between_min_max(data):
    assert min(data) <= statistics.mean(data) <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_equals_value_for_equal_elements(data):
    equal_data = [data[0]] * len(data)
    assert statistics.mean(equal_data) == data[0]

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_multiplied_by_constant(data, constant):
    multiplied_data = [x * constant for x in data]
    assert statistics.mean(multiplied_data) == statistics.mean(data) * constant

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_increased_by_constant(data, constant):
    increased_data = [x + constant for x in data]
    assert statistics.mean(increased_data) == statistics.mean(data) + constant

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_of_concatenated_data(data1, data2):
    concatenated_data = data1 + data2
    weighted_mean = (statistics.mean(data1) * len(data1) + statistics.mean(data2) * len(data2)) / (len(data1) + len(data2))
    assert statistics.mean(concatenated_data) == weighted_mean
# End program