from hypothesis import given, strategies as st
import statistics
import math

# Strategy for positive floats, bounded to avoid overflow/underflow issues
positive_floats = st.floats(
    min_value=1e-6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Non-empty lists of positive floats, bounded in size to avoid overflow
positive_lists = st.lists(positive_floats, min_size=1, max_size=50)

# Positive scaling constant, bounded
positive_constant = st.floats(
    min_value=1e-3,
    max_value=1e3,
    allow_nan=False,
    allow_infinity=False,
)


@given(positive_lists)
def test_statistics_geometric_mean_is_positive(data):
    result = statistics.geometric_mean(data)
    assert result > 0


@given(positive_lists)
def test_statistics_geometric_mean_within_bounds(data):
    result = statistics.geometric_mean(data)
    lo = min(data)
    hi = max(data)
    # Allow small relative tolerance for floating point error
    assert result >= lo * (1 - 1e-9) - 1e-9
    assert result <= hi * (1 + 1e-9) + 1e-9


@given(positive_floats, st.integers(min_value=1, max_value=50))
def test_statistics_geometric_mean_all_equal(value, count):
    data = [value] * count
    result = statistics.geometric_mean(data)
    assert math.isclose(result, value, rel_tol=1e-9, abs_tol=1e-9)


@given(positive_lists, positive_constant)
def test_statistics_geometric_mean_scaling(data, c):
    base = statistics.geometric_mean(data)
    scaled = statistics.geometric_mean([c * x for x in data])
    assert math.isclose(scaled, c * base, rel_tol=1e-9, abs_tol=1e-9)


@given(positive_lists, st.randoms())
def test_statistics_geometric_mean_permutation_invariant(data, rng):
    shuffled = data[:]
    rng.shuffle(shuffled)
    original = statistics.geometric_mean(data)
    permuted = statistics.geometric_mean(shuffled)
    assert math.isclose(original, permuted, rel_tol=1e-9, abs_tol=1e-9)
# End program