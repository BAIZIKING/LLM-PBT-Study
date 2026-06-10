from hypothesis import given, strategies as st
from hypothesis import assume
import statistics
import math

# Strategy for generating reasonable real-valued numbers (avoiding overflow/NaN/inf)
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Lists of at least two values
data_lists = st.lists(finite_floats, min_size=2, max_size=50)


@given(data=data_lists)
def test_statistics_variance_non_negativity(data):
    # Property 1: Variance is always >= 0 for valid input.
    result = statistics.variance(data)
    assert result >= -1e-9  # allow tiny negative due to floating point
# End program


@given(
    value=finite_floats,
    n=st.integers(min_value=2, max_value=50),
)
def test_statistics_variance_zero_for_constant(value, n):
    # Property 2: Variance of constant data is exactly zero.
    data = [value] * n
    result = statistics.variance(data)
    assert math.isclose(result, 0.0, abs_tol=1e-9)
# End program


@given(data=data_lists)
def test_statistics_variance_equivalence_with_explicit_mean(data):
    # Property 3: variance(data) == variance(data, mean(data)).
    xbar = statistics.mean(data)
    without_mean = statistics.variance(data)
    with_mean = statistics.variance(data, xbar)
    assert math.isclose(without_mean, with_mean, rel_tol=1e-9, abs_tol=1e-9)
# End program


@given(
    data=data_lists,
    c=finite_floats,
)
def test_statistics_variance_translation_invariance(data, c):
    # Property 4: Adding a constant to every element leaves variance unchanged.
    original = statistics.variance(data)
    shifted = statistics.variance([x + c for x in data])
    assert math.isclose(original, shifted, rel_tol=1e-6, abs_tol=1e-6)
# End program


@given(
    data=data_lists,
    k=st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
)
def test_statistics_variance_scaling_property(data, k):
    # Property 5: Multiplying every element by k scales variance by k^2.
    original = statistics.variance(data)
    scaled = statistics.variance([x * k for x in data])
    expected = (k ** 2) * original
    assert math.isclose(scaled, expected, rel_tol=1e-6, abs_tol=1e-6)
# End program