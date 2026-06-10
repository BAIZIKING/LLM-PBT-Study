from hypothesis import given, strategies as st, assume
import math
import statistics

# Summary: Generate equal-length lists (len >= 2) of bounded finite floats for x and y,
# along with a random `proportional` flag. Detect constant-x and short-input cases and
# assert StatisticsError; otherwise verify the returned slope/intercept are finite,
# the intercept is 0.0 in proportional mode, and the fitted line produces finite predictions.
@given(st.data())
def test_statistics_linear_regression(data):
    n = data.draw(st.integers(min_value=2, max_value=50), label="n")
    finite_floats = st.floats(
        allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6, width=64
    )
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n), label="x")
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n), label="y")
    proportional = data.draw(st.booleans(), label="proportional")

    x_is_constant = all(xi == x[0] for xi in x)

    if x_is_constant:
        # Constant independent variable must raise StatisticsError.
        try:
            statistics.linear_regression(x, y, proportional=proportional)
            assert False, "Expected StatisticsError for constant x"
        except statistics.StatisticsError:
            return

    result = statistics.linear_regression(x, y, proportional=proportional)

    # Property 1: result exposes finite slope and intercept.
    slope = result.slope
    intercept = result.intercept
    assert math.isfinite(slope), f"slope not finite: {slope}"
    assert math.isfinite(intercept), f"intercept not finite: {intercept}"

    # Property 2: proportional mode forces intercept == 0.0.
    if proportional:
        assert intercept == 0.0, f"expected intercept 0.0 in proportional mode, got {intercept}"

    # Property 3: the fitted line yields finite predictions for all x.
    for xi in x:
        pred = slope * xi + intercept
        assert math.isfinite(pred), f"prediction not finite for x={xi}: {pred}"


# Also verify the length-< 2 edge case separately.
@given(
    st.lists(
        st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
        min_size=0,
        max_size=1,
    )
)
def test_statistics_linear_regression_short_input(short):
    try:
        statistics.linear_regression(short, short)
        assert False, "Expected StatisticsError for input shorter than 2"
    except statistics.StatisticsError:
        pass
# End program