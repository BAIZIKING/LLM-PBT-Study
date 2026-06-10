from hypothesis import given, strategies as st
import statistics

# Define strategies for generating data
list_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)  # Avoid NaN and infinity


@given(list_strategy, list_strategy)
def test_correlation_range(x, y):
    """Output Range: Correlation coefficient should be between -1 and 1 (inclusive)."""
    correlation = statistics.correlation(x, y)
    assert -1 <= correlation <= 1


@given(list_strategy, list_strategy)
def test_correlation_symmetry(x, y):
    """Symmetry: Correlation(X, Y) == Correlation(Y, X)"""
    assert statistics.correlation(x, y) == statistics.correlation(y, x)


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_correlation_constant_input(value):
    """Constant Input: Correlation of constant lists should be NaN."""
    constant_list = [value] * 5  # Create a list with the same value repeated
    assert math.isnan(statistics.correlation(constant_list, constant_list))


@given(list_strategy)
def test_spearman_correlation_monotonic_relationship(data):
    """Monotonic Relationship (Spearman): Order-preserving rearrangements don't change correlation."""
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    assert statistics.correlation(data, shuffled_data, method='ranked') == 1.0


@given(list_strategy, st.floats(allow_nan=False, allow_infinity=False))
def test_pearson_correlation_scaling(data, factor):
    """Linear Relationship (Pearson): Scaling both lists doesn't change correlation."""
    scaled_data = [x * factor for x in data]
    assert statistics.correlation(data, scaled_data) == statistics.correlation(data, data)

# End program