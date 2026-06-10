from hypothesis import given, strategies as st
import statistics

# 1. Test that output is a float between -1 and 1
@given(st.lists(st.floats()), st.lists(st.floats()))
def test_correlation_output_range(x, y):
    if len(x) == len(y) >= 2:
        result = statistics.correlation(x, y)
        assert isinstance(result, float)
        assert -1 <= result <= 1

# 2. Test that function doesn't throw a StatisticsError for valid inputs
@given(st.lists(st.floats(), min_size=2), st.lists(st.floats(), min_size=2))
def test_correlation_no_error(x, y):
    if len(x) == len(y):
        try:
            statistics.correlation(x, y)
        except StatisticsError:
            pytest.fail("Unexpected StatisticsError!")

# 3. Test that sequences are neither constant nor identical for method="linear"
@given(st.lists(st.floats(min_value=1, max_value=1), min_size=2), st.lists(st.floats(min_value=1, max_value=1), min_size=2))
def test_correlation_constant_input(x, y):
    try:
        statistics.correlation(x, y, method='linear')
    except ValueError:
        pytest.fail("Unexpected ValueError!")

# 4. Test that perfect linear relation results in correlation of 1 or -1
@given(st.lists(st.floats(), min_size=2))
def test_correlation_perfect_linear(x):
    y = [i * 2 for i in x]
    assert statistics.correlation(x, y) in {-1.0, 1.0}

# 5. Test that perfect monotonic relation results in corresponding correlation
@given(st.lists(st.integers(), min_size=2))
def test_correlation_perfect_monotonic(x):
    y = sorted(x)
    assert statistics.correlation(y, y, method='ranked') == 1.0