from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate a shared length (>=2), then two equal-length lists of finite,
# bounded floats, and a proportional flag. We construct y from a known linear
# relationship so we can verify parameter recovery, and we also verify the
# constant-x error, the zero-intercept property under proportional, and finiteness.
@given(st.data())
def test_statistics_linear_regression(data):
    n = data.draw(st.integers(min_value=2, max_value=50))

    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False,
    )

    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    proportional = data.draw(st.booleans())

    # Decide whether to build y from a known linear model, or use arbitrary y.
    use_known_model = data.draw(st.booleans())

    if use_known_model:
        true_slope = data.draw(finite_floats)
        true_intercept = 0.0 if proportional else data.draw(finite_floats)
        y = [true_slope * xi + true_intercept for xi in x]
    else:
        true_slope = None
        true_intercept = None
        y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))

    x_is_constant = all(xi == x[0] for xi in x)

    if x_is_constant:
        # Property: constant x must raise StatisticsError.
        try:
            statistics.linear_regression(x, y, proportional=proportional)
            assert False, "Expected StatisticsError for constant x"
        except statistics.StatisticsError:
            return  # correct behavior, nothing more to check

    # x is non-constant: regression should succeed.
    try:
        result = statistics.linear_regression(x, y, proportional=proportional)
    except statistics.StatisticsError:
        # Acceptable only for degenerate proportional cases (e.g. all x effectively
        # collapsing); otherwise re-raise to surface unexpected errors.
        if proportional:
            return
        raise

    # Property: result has slope and intercept (named tuple, unpackable).
    slope, intercept = result
    assert slope == result.slope
    assert intercept == result.intercept

    # Property: returned parameters are finite.
    assert math.isfinite(slope), f"slope not finite: {slope}"
    assert math.isfinite(intercept), f"intercept not finite: {intercept}"

    # Property: proportional => intercept is exactly 0.0.
    if proportional:
        assert intercept == 0.0, f"proportional intercept must be 0.0, got {intercept}"

    # Property: recover known linear parameters within tolerance.
    if use_known_model:
        if not proportional:
            # Compare predicted values against the true model at the data points.
            for xi in x:
                predicted = slope * xi + intercept
                expected = true_slope * xi + true_intercept
                assert math.isclose(predicted, expected, rel_tol=1e-6, abs_tol=1e-3), (
                    f"prediction mismatch: predicted={predicted}, expected={expected}"
                )
        else:
            # For proportional fit through origin with exact data, slope should match.
            for xi in x:
                predicted = slope * xi
                expected = true_slope * xi
                assert math.isclose(predicted, expected, rel_tol=1e-6, abs_tol=1e-3), (
                    f"proportional prediction mismatch: {predicted} vs {expected}"
                )
# End program