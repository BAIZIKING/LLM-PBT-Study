from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists of at least two bounded, finite floats (covering
# constant lists, small lists, and varied magnitudes). Verify non-negativity,
# zero variance for constant data, agreement when passing the precomputed mean
# as xbar, the Bessel-correction relation to pvariance, and translation invariance.
@given(st.data())
def test_statistics_variance():
    data = st.data()  # placeholder to satisfy decorator signature; real draw below

# The actual test (hypothesis injects the data object):
@given(st.data())
def test_statistics_variance(data):
    finite_floats = st.floats(
        allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6
    )
    values = data.draw(st.lists(finite_floats, min_size=2, max_size=50))

    var = statistics.variance(values)

    # Property 1: variance is non-negative.
    assert var >= -1e-9

    # Property 2: constant data has zero variance.
    if len(set(values)) == 1:
        assert math.isclose(var, 0.0, abs_tol=1e-6)

    # Property 3: passing the precomputed mean as xbar gives the same result.
    m = statistics.mean(values)
    var_with_xbar = statistics.variance(values, m)
    assert math.isclose(var, var_with_xbar, rel_tol=1e-9, abs_tol=1e-9)

    # Property 4: Bessel's correction -> variance == pvariance * n / (n - 1).
    n = len(values)
    pvar = statistics.pvariance(values)
    expected = pvar * n / (n - 1)
    assert math.isclose(var, expected, rel_tol=1e-9, abs_tol=1e-9)

    # Property 5: translation invariance (shift all values by a constant).
    shift = data.draw(finite_floats)
    shifted = [x + shift for x in values]
    var_shifted = statistics.variance(shifted)
    scale = max(1.0, abs(var))
    assert math.isclose(var, var_shifted, rel_tol=1e-6, abs_tol=1e-6 * scale)
# End program