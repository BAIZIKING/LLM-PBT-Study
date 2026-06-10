from hypothesis import given, strategies as st, assume
import statistics
import math

# A reasonable float strategy that avoids NaN, infinity, and overly large
# magnitudes that could cause overflow when squaring/cubing internally.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

def _is_constant(seq):
    return all(v == seq[0] for v in seq)

def _paired_lists(data, min_size=2, max_size=50):
    n = data.draw(st.integers(min_value=min_size, max_value=max_size))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    return x, y


@given(st.data())
def test_statistics_correlation_property_bounded():
    # Property 1: output is a float bounded within [-1, +1].
    @given(st.data())
    def inner(data):
        x, y = _paired_lists(data)
        assume(not _is_constant(x))
        assume(not _is_constant(y))
        for method in ('linear', 'ranked'):
            r = statistics.correlation(x, y, method=method)
            assert isinstance(r, float)
            # Allow tiny floating point tolerance beyond the bounds.
            assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9
    inner()


@given(st.data())
def test_statistics_correlation_property_symmetric():
    # Property 2: symmetry in the two arguments.
    @given(st.data())
    def inner(data):
        x, y = _paired_lists(data)
        assume(not _is_constant(x))
        assume(not _is_constant(y))
        for method in ('linear', 'ranked'):
            r_xy = statistics.correlation(x, y, method=method)
            r_yx = statistics.correlation(y, x, method=method)
            assert math.isclose(r_xy, r_yx, rel_tol=1e-9, abs_tol=1e-9)
    inner()


@given(st.data())
def test_statistics_correlation_property_self():
    # Property 3: correlation of a non-constant variable with itself is +1.0.
    @given(st.data())
    def inner(data):
        n = data.draw(st.integers(min_value=2, max_value=50))
        x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
        assume(not _is_constant(x))
        for method in ('linear', 'ranked'):
            r = statistics.correlation(x, x, method=method)
            assert math.isclose(r, 1.0, rel_tol=1e-9, abs_tol=1e-9)
    inner()


@given(st.data())
def test_statistics_correlation_property_linear_transform():
    # Property 4: positive linear transform leaves result unchanged;
    # negative scaling negates it (for the linear method).
    @given(st.data())
    def inner(data):
        x, y = _paired_lists(data)
        assume(not _is_constant(x))
        assume(not _is_constant(y))
        # Scale factor (nonzero) and offset, kept modest to avoid overflow.
        a = data.draw(st.floats(min_value=-100.0, max_value=100.0,
                                allow_nan=False, allow_infinity=False))
        assume(abs(a) > 1e-3)
        b = data.draw(st.floats(min_value=-100.0, max_value=100.0,
                                allow_nan=False, allow_infinity=False))
        y_transformed = [a * v + b for v in y]
        assume(not _is_constant(y_transformed))

        r_orig = statistics.correlation(x, y, method='linear')
        r_trans = statistics.correlation(x, y_transformed, method='linear')

        expected = r_orig if a > 0 else -r_orig
        assert math.isclose(r_trans, expected, rel_tol=1e-6, abs_tol=1e-6)
    inner()


@given(st.data())
def test_statistics_correlation_property_monotonic_ranked():
    # Property 5: for a strictly monotonic (possibly nonlinear) relationship,
    # the ranked method returns exactly +1.0 (increasing) or -1.0 (decreasing).
    @given(st.data())
    def inner(data):
        n = data.draw(st.integers(min_value=2, max_value=50))
        # Generate strictly increasing distinct x values.
        raw = data.draw(st.lists(finite_floats, min_size=n, max_size=n,
                                 unique=True))
        x = sorted(raw)
        assume(not _is_constant(x))
        # Build a strictly increasing nonlinear y via a monotonic transform.
        increasing = data.draw(st.booleans())
        # Use a strictly increasing function (cube) to preserve order.
        y = [v ** 3 for v in x]
        if not increasing:
            y = list(reversed(y))
        assume(not _is_constant(y))

        r = statistics.correlation(x, y, method='ranked')
        if increasing:
            assert math.isclose(r, 1.0, rel_tol=1e-9, abs_tol=1e-9)
        else:
            assert math.isclose(r, -1.0, rel_tol=1e-9, abs_tol=1e-9)
    inner()
# End program