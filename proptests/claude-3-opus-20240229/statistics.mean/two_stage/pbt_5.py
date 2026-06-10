from hypothesis import given, strategies as st
import statistics
from math import isclose

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_within_bounds(data):
    mean = statistics.mean(data)
    assert min(data) <= mean <= max(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_equals_sum_divided_by_length(data):
    mean = statistics.mean(data)
    assert isclose(mean, sum(data) / len(data))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_invariant_to_order(data):
    mean1 = statistics.mean(data)
    data.reverse()
    mean2 = statistics.mean(data)
    assert isclose(mean1, mean2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_adding_mean_to_dataset(data):
    mean1 = statistics.mean(data)
    data.append(mean1)
    mean2 = statistics.mean(data)
    assert isclose(mean1, mean2)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats())
def test_multiplying_dataset_by_constant(data, constant):
    mean1 = statistics.mean(data)
    data = [x * constant for x in data]
    mean2 = statistics.mean(data)
    assert isclose(mean1 * constant, mean2)
# End program