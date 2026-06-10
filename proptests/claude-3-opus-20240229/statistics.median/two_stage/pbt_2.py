from hypothesis import given, strategies as st
from hypothesis.errors import HypothesisDeprecationWarning
import statistics
import warnings

warnings.filterwarnings("ignore", category=HypothesisDeprecationWarning)

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1))
def test_median_within_range(data):
    median = statistics.median(data)
    assert min(data) <= median <= max(data)

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1))
def test_median_sorted_data(data):
    sorted_data = sorted(data)
    median = statistics.median(sorted_data)
    n = len(sorted_data)
    if n % 2 == 1:
        assert median == sorted_data[n // 2]
    else:
        assert median == (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1))
def test_median_permutation_invariance(data):
    median1 = statistics.median(data)
    data_perm = data[:]
    data_perm.reverse()
    median2 = statistics.median(data_perm)
    assert median1 == median2

@given(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=1))
def test_median_adding_element(data):
    median = statistics.median(data)
    data.append(median)
    new_median = statistics.median(data)
    assert median == new_median

@given(st.floats(allow_infinity=False, allow_nan=False), st.integers(min_value=1, max_value=100))
def test_median_identical_elements(value, size):
    data = [value] * size
    median = statistics.median(data)
    assert median == value
# End program