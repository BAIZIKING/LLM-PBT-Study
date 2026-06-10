from hypothesis import given, strategies as st, assume
import statistics
import math

# Summary: Draw a shared length (>=2), build two equal-length lists of finite,
# bounded numbers, pick a method, and also construct derived data (affine and
# monotonic transforms) to verify documented properties: the coefficient is
# bounded in [-1, 1], perfect +/-1 for affine relations under 'linear', perfect
# 1.0 for monotonic relations under 'ranked', symmetry, and StatisticsError for
# constant inputs.
@given(st.data())
def test_statistics_correlation(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    finite = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False,
    )
    x = data.draw(st.lists(finite, min_size=n, max_size=n))
    y = data.draw(st.lists(finite, min_size=n, max_size=n))
    method = data.draw(st.sampled_from(['linear', 'ranked']))

    # Determine constancy (must be non-constant to avoid StatisticsError)
    x_constant = len(set(x)) <= 1
    y_constant = len(set(y)) <= 1

    # Property 6: Constant inputs must raise StatisticsError.
    if x_constant or y_constant:
        try:
            statistics.correlation(x, y, method=method)
            assert False, "Expected StatisticsError for constant input"
        except statistics.StatisticsError:
            return
        return

    # Both non-constant: compute correlation.
    r = statistics.correlation(x, y, method=method)

    # Property 1: Result must be bounded in [-1, 1] (allow tiny float slack).
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9

    # Property 5: Symmetry of correlation.
    r_swapped = statistics.correlation(y, x, method=method)
    assert math.isclose(r, r_swapped, rel_tol=1e-9, abs_tol=1e-9)

    # Property 2 & 3: Perfect linear correlation for an affine transform.
    # Build y2 = a*x + b with a strictly positive or negative slope.
    a = data.draw(st.floats(min_value=0.1, max_value=100,
                            allow_nan=False, allow_infinity=False))
    b = data.draw(st.floats(min_value=-1000, max_value=1000,
                            allow_nan=False, allow_infinity=False))
    sign = data.draw(st.sampled_from([1.0, -1.0]))
    a_signed = sign * a
    y2 = [a_signed * xi + b for xi in x]
    # y2 is non-constant since x is non-constant and a_signed != 0.
    if len(set(y2)) > 1:
        r_lin = statistics.correlation(x, y2, method='linear')
        expected = 1.0 if a_signed > 0 else -1.0
        assert math.isclose(r_lin, expected, rel_tol=1e-6, abs_tol=1e-6)

    # Property 4: Perfect monotonic (ranked) correlation for a strictly
    # increasing transform. Sort x to assign ranks, build a strictly
    # increasing y3 (1, 2, 3, ...) and check ranked correlation == 1.0.
    # Use distinct x values to avoid ties in the rank check.
    distinct_x = sorted(set(x))
    if len(distinct_x) >= 2:
        # Map each x value to its rank position to build monotone y3.
        rank_of = {v: i for i, v in enumerate(distinct_x)}
        y3 = [float(rank_of[xi]) for xi in x]
        if len(set(y3)) > 1:
            r_ranked = statistics.correlation(x, y3, method='ranked')
            assert math.isclose(r_ranked, 1.0, rel_tol=1e-9, abs_tol=1e-9)
# End program