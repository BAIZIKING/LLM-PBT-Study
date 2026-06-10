from hypothesis import given, strategies as st
import statistics
import math

# Strategy for finite floats with bounded magnitude to avoid overflow issues
finite_floats = st.floats(
    min_value=-1e9,
    max_value=1e9,
    allow_nan=False,
    allow_infinity=False,
)

# Non-empty list strategy
nonempty_float_lists = st.lists(finite_floats, min_size=1, max_size=100)


@given(data=nonempty_float_lists)
def test_statistics_mean_within_bounds(data):
    # Property 1: The mean always lies between the min and max of the data (inclusive).
    result = statistics.mean(data)
    lo = min(data)
    hi = max(data)
    # Allow tiny floating point tolerance at the boundaries
    tol = 1e-6 * (abs(hi) + abs(lo) + 1.0)
    assert lo - tol <= result <= hi + tol


@given(value=finite_floats, n=st.integers(min_value=1, max_value=100))
def test_statistics_mean_repeated_value(value, n):
    # Property 2: The mean of a list of a single repeated value equals that value.
    data = [value] * n
    result = statistics.mean(data)
    assert math.isclose(result, value, rel_tol=1e-9, abs_tol=1e-9)


@given(data=nonempty_float_lists, c=finite_floats)
def test_statistics_mean_add_constant(data, c):
    # Property 3: Adding a constant c to every element increases the mean by c.
    base_mean = statistics.mean(data)
    shifted_mean = statistics.mean([x + c for x in data])
    expected = base_mean + c
    tol = 1e-6 * (abs(expected) + abs(base_mean) + abs(c) + 1.0)
    assert math.isclose(shifted_mean, expected, rel_tol=1e-6, abs_tol=tol)


@given(data=nonempty_float_lists, c=finite_floats)
def test_statistics_mean_multiply_constant(data, c):
    # Property 4: Multiplying every element by c multiplies the mean by c.
    base_mean = statistics.mean(data)
    scaled_mean = statistics.mean([x * c for x in data])
    expected = base_mean * c
    tol = 1e-6 * (abs(expected) + abs(scaled_mean) + 1.0)
    assert math.isclose(scaled_mean, expected, rel_tol=1e-6, abs_tol=tol)


@given(data=nonempty_float_lists)
def test_statistics_mean_times_count_equals_sum(data):
    # Property 5: mean(data) * len(data) == sum(data).
    result = statistics.mean(data)
    product = result * len(data)
    total = sum(data)
    tol = 1e-6 * (abs(total) + abs(product) + 1.0)
    assert math.isclose(product, total, rel_tol=1e-6, abs_tol=tol)
# End program