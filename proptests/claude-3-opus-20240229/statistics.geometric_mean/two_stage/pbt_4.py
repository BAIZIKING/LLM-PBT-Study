from hypothesis import given, strategies as st
from hypothesis.errors import HypothesisDeprecationWarning
from hypothesis.extra.numpy import arrays
import statistics
import pytest

@given(st.lists(st.floats(min_value=0.0, max_value=1e100, allow_infinity=False, allow_nan=False), min_size=1))
def test_geometric_mean_bounds(data):
    result = statistics.geometric_mean(data)
    assert min(data) <= result <= max(data)

@given(st.lists(st.floats(min_value=0.0, max_value=1e100, allow_infinity=False, allow_nan=False), min_size=1))
def test_geometric_mean_identical_values(data):
    identical_value = data[0]
    data = [identical_value] * len(data)
    result = statistics.geometric_mean(data)
    assert result == identical_value

@given(st.lists(st.floats(min_value=0.0, max_value=1e100, allow_infinity=False, allow_nan=False), min_size=1), st.floats(min_value=0.0, max_value=1e100))
def test_geometric_mean_multiplicative_property(data, constant):
    result1 = statistics.geometric_mean(data)
    result2 = statistics.geometric_mean([x * constant for x in data])
    assert pytest.approx(result1 * constant) == result2

@given(st.lists(st.floats(max_value=-0.0, max_value=1e100, allow_infinity=False, allow_nan=False)))
def test_geometric_mean_empty_data(data):
    with pytest.raises(statistics.StatisticsError):
        statistics.geometric_mean(data)

@given(st.lists(st.floats(min_value=-1e100, max_value=1e100, allow_infinity=False, allow_nan=False), min_size=1))
def test_geometric_mean_negative_zero_values(data):
    with pytest.raises(statistics.StatisticsError):
        statistics.geometric_mean(data)
# End program