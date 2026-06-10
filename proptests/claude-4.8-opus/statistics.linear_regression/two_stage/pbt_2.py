from hypothesis import given, strategies as st, assume
import statistics
import math
import pytest

# Strategy for finite, bounded floats to avoid overflows in least-squares computations
reasonable_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


# Property 1: The function returns two finite real numbers for slope and intercept.
@given(st.data())
def test_returns_two_finite_numbers():
    n = data_n = None
    # build a paired list of length >= 2 with non-constant x
    n = 5
    xs = []
    ys = []
    # We use a data strategy via @given below instead; placeholder removed.
    pass


@given(
    xs=st.lists(reasonable_floats, min_size=2, max_size=50),
    data=st.data(),
)
def test_returns_two_finite_numbers_real(xs, data):
    # x must not be constant
    assume(len(set(xs)) > 1)
    ys = data.draw(
        st.lists(reasonable_floats, min_size=len(xs), max_size=len(xs))
    )
    result = statistics.linear_regression(xs, ys)
    slope, intercept = result
    assert isinstance(slope, float) and isinstance(intercept, float)
    assert math.isfinite(slope)
    assert math.isfinite(intercept)


# Property 2: When proportional=True, the intercept is always exactly 0.0.
@given(
    xs=st.lists(reasonable_floats, min_size=2, max_size=50),
    data=st.data(),
)
def test_proportional_intercept_is_zero(xs, data):
    assume(len(set(xs)) > 1)
    ys = data.draw(
        st.lists(reasonable_floats, min_size=len(xs), max_size=len(xs))
    )
    result = statistics.linear_regression(xs, ys, proportional=True)
    assert result.intercept == 0.0


# Property 3: For proportional=False, the fitted line passes through the centroid.
@given(
    xs=st.lists(reasonable_floats, min_size=2, max_size=50),
    data=st.data(),
)
def test_line_passes_through_centroid(xs, data):
    assume(len(set(xs)) > 1)
    ys = data.draw(
        st.lists(reasonable_floats, min_size=len(xs), max_size=len(xs))
    )
    slope, intercept = statistics.linear_regression(xs, ys)
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    predicted = slope * mean_x + intercept
    tol = 1e-6 * (1 + abs(mean_y) + abs(slope * mean_x))
    assert math.isclose(predicted, mean_y, abs_tol=tol, rel_tol=1e-6)


# Property 4: Exact linear data recovers the true slope and intercept.
@given(
    xs=st.lists(reasonable_floats, min_size=2, max_size=50, unique=True),
    a=reasonable_floats,
    b=reasonable_floats,
)
def test_recovers_exact_linear_relationship(xs, a, b):
    assume(len(set(xs)) > 1)
    ys = [a * x + b for x in xs]
    # ensure ys are finite and bounded
    assume(all(math.isfinite(y) and abs(y) < 1e12 for y in ys))
    slope, intercept = statistics.linear_regression(xs, ys)
    # spread of x must be large enough for numerical stability
    spread = max(xs) - min(xs)
    assume(spread > 1e-3)
    tol_slope = 1e-4 * (1 + abs(a))
    tol_intercept = 1e-4 * (1 + abs(b) + abs(a) * (abs(max(xs)) + 1))
    assert math.isclose(slope, a, abs_tol=tol_slope, rel_tol=1e-4)
    assert math.isclose(intercept, b, abs_tol=tol_intercept, rel_tol=1e-4)


# Property 5: StatisticsError raised for mismatched lengths, too-short, or constant x.
@given(st.data())
def test_raises_statistics_error(data):
    case = data.draw(st.sampled_from(["mismatch", "too_short", "constant_x"]))
    if case == "mismatch":
        xs = data.draw(st.lists(reasonable_floats, min_size=2, max_size=10))
        # ensure x is non-constant so the error is purely about length
        assume(len(set(xs)) > 1)
        ys = data.draw(
            st.lists(reasonable_floats, min_size=0, max_size=10).filter(
                lambda lst: len(lst) != len(xs)
            )
        )
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(xs, ys)
    elif case == "too_short":
        # length 0 or 1
        single = data.draw(st.lists(reasonable_floats, min_size=0, max_size=1))
        ys = data.draw(
            st.lists(reasonable_floats, min_size=len(single), max_size=len(single))
        )
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(single, ys)
    else:  # constant_x
        n = data.draw(st.integers(min_value=2, max_value=20))
        const = data.draw(reasonable_floats)
        xs = [const] * n
        ys = data.draw(st.lists(reasonable_floats, min_size=n, max_size=n))
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(xs, ys)
# End program