from hypothesis import given, strategies as st, assume
import statistics
import math
import pytest


# A reasonable strategy for floats that avoids NaN, infinities, and
# excessively large magnitudes that could cause overflow in the OLS computation.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


def paired_lists(min_size=2, max_size=50):
    """Generate two equal-length lists of floats."""
    return st.lists(
        st.tuples(finite_floats, finite_floats),
        min_size=min_size,
        max_size=max_size,
    ).map(lambda pairs: ([p[0] for p in pairs], [p[1] for p in pairs]))


# Property 1: The result has finite slope and intercept for valid inputs.
@given(paired_lists())
def test_result_is_finite(data):
    x, y = data
    # x must not be constant
    assume(len(set(x)) > 1)
    result = statistics.linear_regression(x, y)
    assert math.isfinite(result.slope)
    assert math.isfinite(result.intercept)


# Property 2: When proportional=True, intercept is always exactly 0.0.
@given(paired_lists())
def test_proportional_intercept_zero(data):
    x, y = data
    assume(len(set(x)) > 1)
    result = statistics.linear_regression(x, y, proportional=True)
    assert result.intercept == 0.0


# Property 3: The fitted line passes through the mean point of the data.
@given(paired_lists())
def test_line_passes_through_mean(data):
    x, y = data
    assume(len(set(x)) > 1)
    slope, intercept = statistics.linear_regression(x, y)
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)
    predicted_mean_y = slope * mean_x + intercept
    # Use a tolerance scaled to the magnitudes involved.
    tol = 1e-6 * (1 + abs(mean_y) + abs(slope * mean_x))
    assert math.isclose(predicted_mean_y, mean_y, abs_tol=tol, rel_tol=1e-6)


# Property 4: Data lying exactly on a line is recovered by the regression.
@given(
    st.lists(finite_floats, min_size=2, max_size=50, unique=True),
    finite_floats,  # slope a
    finite_floats,  # intercept b
)
def test_recovers_exact_line(xs, a, b):
    # xs is unique => x is not constant
    ys = [a * x + b for x in xs]
    # Avoid overflow / extreme magnitudes in constructed y values.
    assume(all(math.isfinite(y) and abs(y) < 1e12 for y in ys))
    slope, intercept = statistics.linear_regression(xs, ys)
    # Check predicted values reproduce the original y values.
    for x, y in zip(xs, ys):
        pred = slope * x + intercept
        tol = 1e-4 * (1 + abs(y))
        assert math.isclose(pred, y, abs_tol=tol, rel_tol=1e-4)


# Property 5: Errors are raised for invalid inputs.
@given(st.data())
def test_invalid_inputs_raise(data):
    # Case A: mismatched lengths
    x_a = data.draw(st.lists(finite_floats, min_size=2, max_size=10))
    y_a = data.draw(st.lists(finite_floats, min_size=2, max_size=10))
    if len(x_a) != len(y_a):
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(x_a, y_a)

    # Case B: fewer than two elements
    single = data.draw(st.lists(finite_floats, min_size=0, max_size=1))
    with pytest.raises(statistics.StatisticsError):
        statistics.linear_regression(single, single)

    # Case C: constant x
    n = data.draw(st.integers(min_value=2, max_value=10))
    const_val = data.draw(finite_floats)
    x_c = [const_val] * n
    y_c = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    with pytest.raises(statistics.StatisticsError):
        statistics.linear_regression(x_c, y_c)
# End program