from hypothesis import given, strategies as st, assume
import statistics
import math

# Finite, bounded floats to avoid overflow when computing sums of products.
safe_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


def _is_constant(seq):
    return all(v == seq[0] for v in seq)


@given(st.data())
def test_statistics_correlation_bounded_output():
    # Property 1: result is a float within [-1, 1] for any valid input.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    assume(not _is_constant(x))
    assume(not _is_constant(y))
    method = data.draw(st.sampled_from(["linear", "ranked"]))
    r = statistics.correlation(x, y, method=method)
    assert isinstance(r, float)
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9


@given(st.data())
def test_statistics_correlation_symmetry():
    # Property 2: correlation(x, y) == correlation(y, x).
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    assume(not _is_constant(x))
    assume(not _is_constant(y))
    method = data.draw(st.sampled_from(["linear", "ranked"]))
    r_xy = statistics.correlation(x, y, method=method)
    r_yx = statistics.correlation(y, x, method=method)
    assert math.isclose(r_xy, r_yx, rel_tol=1e-9, abs_tol=1e-9)


@given(st.data())
def test_statistics_correlation_perfect_positive_linear():
    # Property 3: y = a*x + b with a > 0 yields linear correlation 1.0;
    # also correlation(x, x) == 1.0.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    assume(not _is_constant(x))
    a = data.draw(st.floats(min_value=1e-3, max_value=1e3,
                            allow_nan=False, allow_infinity=False))
    b = data.draw(st.floats(min_value=-1e3, max_value=1e3,
                            allow_nan=False, allow_infinity=False))
    y = [a * xi + b for xi in x]
    assume(not _is_constant(y))
    r = statistics.correlation(x, y, method="linear")
    assert math.isclose(r, 1.0, rel_tol=1e-7, abs_tol=1e-7)
    r_self = statistics.correlation(x, x, method="linear")
    assert math.isclose(r_self, 1.0, rel_tol=1e-7, abs_tol=1e-7)


@given(st.data())
def test_statistics_correlation_perfect_negative_linear():
    # Property 4: y = a*x + b with a < 0 yields linear correlation -1.0.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
    assume(not _is_constant(x))
    a = data.draw(st.floats(min_value=-1e3, max_value=-1e-3,
                            allow_nan=False, allow_infinity=False))
    b = data.draw(st.floats(min_value=-1e3, max_value=1e3,
                            allow_nan=False, allow_infinity=False))
    y = [a * xi + b for xi in x]
    assume(not _is_constant(y))
    r = statistics.correlation(x, y, method="linear")
    assert math.isclose(r, -1.0, rel_tol=1e-7, abs_tol=1e-7)


@given(st.data())
def test_statistics_correlation_perfect_monotonic_ranked():
    # Property 5: strictly increasing transform -> ranked correlation 1.0;
    # strictly decreasing transform -> ranked correlation -1.0.
    n = data.draw(st.integers(min_value=2, max_value=50))
    # Use distinct values so ranks are unambiguous and monotonicity is strict.
    x = data.draw(
        st.lists(safe_floats, min_size=n, max_size=n, unique=True)
    )
    assume(not _is_constant(x))
    increasing = data.draw(st.booleans())
    if increasing:
        # Strictly increasing transform: y = x^3 preserves order of sorted x.
        y = [xi ** 3 for xi in x]
        expected = 1.0
    else:
        # Strictly decreasing transform: y = -x^3 reverses order.
        y = [-(xi ** 3) for xi in x]
        expected = -1.0
    assume(not _is_constant(y))
    r = statistics.correlation(x, y, method="ranked")
    assert math.isclose(r, expected, rel_tol=1e-9, abs_tol=1e-9)
# End program