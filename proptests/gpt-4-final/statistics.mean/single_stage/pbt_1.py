from hypothesis import given, strategies as st
import statistics
import pytest
import math
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_statistics_mean(lst):
    # Property 1: statistics.mean returns correct arithmetic mean
    expected_mean = sum(lst) / len(lst)
    assert math.isclose(statistics.mean(lst), expected_mean, rel_tol=1e-9)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=0))
def test_statistics_mean_empty(lst):
    # Property 2: statistics.mean raises StatisticsError if data set is empty
    with pytest.raises(statistics.StatisticsError):
        statistics.mean(lst)