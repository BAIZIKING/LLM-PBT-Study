from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of floats with reasonable size and range
list_of_floats = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100)

@given(list_of_floats, list_of_floats)
def test_correlation_range(x, y):
    # Check if the correlation coefficient is within the valid range
    corr = statistics.correlation(x, y)
    assert -1 <= corr <= 1

@given(list_of_floats, list_of_floats)
def test_correlation_symmetry(x, y):
    # Check if correlation is symmetric
    corr_xy = statistics.correlation(x, y)
    corr_yx = statistics.correlation(y, x)
    assert corr_xy == corr_yx

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_correlation_constant_input(value):
    # Create constant lists
    x = [value] * 5
    y = [value] * 5
    # Check if correlation is NaN for constant inputs
    corr = statistics.correlation(x, y)
    assert math.isnan(corr)

@given(list_of_floats)
def test_spearman_monotonic_increasing(x):
    # Sort x to create a perfect monotonic increasing relationship
    y = sorted(x)
    # Check if Spearman correlation is 1
    corr = statistics.correlation(x, y, method='ranked')
    assert corr == 1

@given(list_of_floats)
def test_pearson_perfect_linear(x):
    # Create a perfect linear relationship
    y = [2*i + 3 for i in x]
    # Check if Pearson correlation is 1
    corr = statistics.correlation(x, y)
    assert corr == 1
# End program