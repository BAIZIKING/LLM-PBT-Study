from hypothesis import given, strategies as st
from statistics import mean
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_within_bounds(data):
    assert min(data) <= mean(data) <= max(data)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_mean_single_value(x):
    assert mean([x]) == x

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_invariant_to_shuffle(data):
    assert mean(data) == mean(sorted(data))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.floats(allow_nan=False, allow_infinity=False))
def test_mean_linearity(data, scale):
    assert math.isclose(mean([x * scale for x in data]), mean(data) * scale)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_concatenation(data1, data2):
    combined_mean = mean(data1 + data2)
    weighted_mean = (mean(data1) * len(data1) + mean(data2) * len(data2)) / (len(data1) + len(data2))
    assert math.isclose(combined_mean, weighted_mean)
# End program