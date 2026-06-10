from hypothesis import given, strategies as st
from hypothesis import assume
import statistics
import math

# Use a bounded float strategy to avoid overflow and NaN/inf issues.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Property 1: mean is between min and max of the data.
@given(st.lists(finite_floats, min_size=1))
def test_statistics_mean_within_bounds():
    data = ...  # placeholder to satisfy format; real data passed below
    pass

# Property 1: mean is between min and max of the data.
@given(data=st.lists(finite_floats, min_size=1))
def test_statistics_mean_within_bounds(data):
    m = statistics.mean(data)
    # Allow small tolerance for floating point rounding.
    tol = 1e-9 * (1 + abs(max(data)) + abs(min(data)))
    assert min(data) - tol <= m <= max(data) + tol


# Property 2: Adding a constant to every element shifts the mean by that constant.
@given(data=st.lists(finite_floats, min_size=1), c=finite_floats)
def test_statistics_mean_shift_invariance(data):
    pass

@given(data=st.lists(finite_floats, min_size=1), c=finite_floats)
def test_statistics_mean_shift(data, c):
    base = statistics.mean(data)
    shifted = statistics.mean([x + c for x in data])
    expected = base + c
    tol = 1e-6 * (1 + abs(expected))
    assert math.isclose(shifted, expected, rel_tol=1e-6, abs_tol=tol)


# Property 3: Scaling every element by a factor scales the mean by that factor.
@given(
    data=st.lists(finite_floats, min_size=1),
    factor=st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
)
def test_statistics_mean_scale(data, factor):
    base = statistics.mean(data)
    scaled = statistics.mean([x * factor for x in data])
    expected = base * factor
    tol = 1e-6 * (1 + abs(expected))
    assert math.isclose(scaled, expected, rel_tol=1e-6, abs_tol=tol)


# Property 4: The mean of a list of equal values equals that value.
@given(
    value=finite_floats,
    n=st.integers(min_value=1, max_value=1000),
)
def test_statistics_mean_constant_list(value, n):
    data = [value] * n
    m = statistics.mean(data)
    tol = 1e-9 * (1 + abs(value))
    assert math.isclose(m, value, rel_tol=1e-9, abs_tol=tol)


# Property 5: mean * count == sum of data.
@given(data=st.lists(finite_floats, min_size=1))
def test_statistics_mean_times_count_equals_sum(data):
    m = statistics.mean(data)
    total = sum(data)
    product = m * len(data)
    tol = 1e-6 * (1 + abs(total))
    assert math.isclose(product, total, rel_tol=1e-6, abs_tol=tol)
# End program