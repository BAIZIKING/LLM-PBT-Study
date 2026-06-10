from hypothesis import given, assume, strategies as st
import statistics
import math

# Summary: Generate a shared length (>=2), then two equal-length lists of finite,
# bounded floats for x and y, plus a boolean for the `proportional` flag.
# Ensure x is non-constant (assume distinct values) so a valid result is produced.
# Check: result has slope/intercept attributes; intercept==0.0 when proportional;
# outputs are finite floats; and for ordinary OLS the line passes through the
# centroid (mean(y) == slope*mean(x) + intercept).
@given(st.data())
def test_statistics_linear_regression(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False,
    )
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    proportional = data.draw(st.booleans())

    # x must not be constant for a valid result.
    assume(len(set(x)) >= 2)

    result = statistics.linear_regression(x, y, proportional=proportional)

    # Property 1: result has slope and intercept attributes.
    assert hasattr(result, "slope")
    assert hasattr(result, "intercept")

    slope = result.slope
    intercept = result.intercept

    # Property 3: outputs are finite real numbers.
    assert isinstance(slope, float)
    assert isinstance(intercept, float)
    assert math.isfinite(slope)
    assert math.isfinite(intercept)

    if proportional:
        # Property 2: intercept is always exactly 0.0 in proportional mode.
        assert intercept == 0.0
    else:
        # Property 4: OLS line passes through the centroid (mean(x), mean(y)).
        mean_x = statistics.fmean(x)
        mean_y = statistics.fmean(y)
        predicted_mean_y = slope * mean_x + intercept
        assert math.isclose(
            predicted_mean_y, mean_y, rel_tol=1e-6, abs_tol=1e-6
        )
# End program