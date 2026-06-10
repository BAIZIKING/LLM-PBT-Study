from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists of at least 2 finite floats bounded in magnitude (to avoid
# overflow and severe precision loss). Occasionally generate constant lists (all equal
# values) as an edge case. A boolean controls whether the true mean is passed as xbar.
# Properties checked: (1) variance is non-negative, (2) passing the true mean as xbar
# gives the same result as xbar=None, (3) constant data has zero variance, and
# (4) the result matches the Bessel-corrected formula sum((x-mean)^2)/(n-1).
@given(st.data())
def test_statistics_variance(data):
    finite_floats = st.floats(
        allow_nan=False, allow_infinity=False,
        min_value=-1e6, max_value=1e6, width=64
    )

    # Either a general list, or a constant list (edge case), both with size >= 2.
    use_constant = data.draw(st.booleans())
    if use_constant:
        value = data.draw(finite_floats)
        n = data.draw(st.integers(min_value=2, max_value=50))
        values = [value] * n
    else:
        values = data.draw(st.lists(finite_floats, min_size=2, max_size=50))

    mean = statistics.mean(values)
    result = statistics.variance(values)

    # Property 1: variance must be non-negative.
    assert result >= 0

    # Property 2: passing the true mean as xbar yields the same result.
    pass_xbar = data.draw(st.booleans())
    if pass_xbar:
        result_xbar = statistics.variance(values, mean)
        assert math.isclose(result, result_xbar, rel_tol=1e-9, abs_tol=1e-9)

    # Property 3: constant data must have exactly zero variance.
    if use_constant:
        assert result == 0

    # Property 4: result matches Bessel-corrected formula.
    n = len(values)
    expected = sum((x - mean) ** 2 for x in values) / (n - 1)
    assert math.isclose(result, expected, rel_tol=1e-6, abs_tol=1e-6)
# End program