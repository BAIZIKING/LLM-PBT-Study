from hypothesis import given, strategies as st, assume
import math
import statistics

# Summary: Generate a non-constant list of finite, bounded x values (length >= 2),
# pick a known true slope and intercept (intercept forced to 0 when proportional),
# build y = slope*x + intercept exactly (zero noise), and randomly choose the
# proportional flag. Then verify the returned regression reproduces the data:
# predictions equal y within tolerance, intercept is 0.0 when proportional=True,
# and outputs are finite and unpackable.
@given(st.data())
def test_statistics_linear_regression(data):
    # Bounded finite floats to avoid overflow / catastrophic precision loss
    safe_float = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False,
    )

    # x: list of at least 2 finite values
    x = data.draw(st.lists(safe_float, min_size=2, max_size=30))

    # x must not be constant (else StatisticsError); skip degenerate cases
    assume(len(set(x)) > 1)

    proportional = data.draw(st.booleans())

    true_slope = data.draw(safe_float)
    # When proportional, the fitted line passes through origin -> build y with intercept 0
    true_intercept = 0.0 if proportional else data.draw(safe_float)

    # Build y as an exact linear function (zero noise) so true parameters are known
    y = [true_slope * xi + true_intercept for xi in x]

    # Skip if construction produced non-finite values
    assume(all(math.isfinite(yi) for yi in y))

    result = statistics.linear_regression(x, y, proportional=proportional)

    # Property 1: result is unpackable into (slope, intercept) and has attributes
    slope, intercept = result
    assert slope == result.slope
    assert intercept == result.intercept

    # Property 2: outputs are finite for valid finite inputs
    assert math.isfinite(slope)
    assert math.isfinite(intercept)

    # Property 3: intercept must be exactly 0.0 when proportional=True
    if proportional:
        assert intercept == 0.0

    # Property 4: with zero-noise data, predictions must reproduce y within tolerance
    for xi, yi in zip(x, y):
        predicted = slope * xi + intercept
        assert math.isclose(predicted, yi, rel_tol=1e-6, abs_tol=1e-6)
# End program