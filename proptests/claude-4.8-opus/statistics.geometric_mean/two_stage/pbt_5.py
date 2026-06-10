from hypothesis import given, strategies as st
import statistics
import math

# Strategy for positive floats that avoid zero, infinities, NaNs, and overflow risks.
positive_floats = st.floats(
    min_value=1e-6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

@given(data=st.lists(positive_floats, min_size=1))
def test_geometric_mean_is_positive(data):
    result = statistics.geometric_mean(data)
    assert result > 0

@given(value=positive_floats, n=st.integers(min_value=1, max_value=20))
def test_geometric_mean_of_identical_values(value, n):
    data = [value] * n
    result = statistics.geometric_mean(data)
    assert math.isclose(result, value, rel_tol=1e-6)

@given(data=st.lists(positive_floats, min_size=1))
def test_geometric_mean_within_min_max(data):
    result = statistics.geometric_mean(data)
    lo = min(data)
    hi = max(data)
    # Allow small tolerance for floating point inaccuracies at the boundaries.
    assert lo * (1 - 1e-6) <= result <= hi * (1 + 1e-6)

@given(value=positive_floats)
def test_geometric_mean_single_element(value):
    result = statistics.geometric_mean([value])
    assert math.isclose(result, value, rel_tol=1e-6)

@given(
    data=st.lists(positive_floats, min_size=1),
    k=st.floats(min_value=1e-3, max_value=1e3, allow_nan=False, allow_infinity=False),
)
def test_geometric_mean_scaling(data, k):
    base = statistics.geometric_mean(data)
    scaled = statistics.geometric_mean([k * x for x in data])
    assert math.isclose(scaled, k * base, rel_tol=1e-6)
# End program