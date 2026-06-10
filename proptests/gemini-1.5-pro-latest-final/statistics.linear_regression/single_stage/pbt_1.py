from hypothesis import given, strategies as st
import statistics

# Summary: Generate diverse inputs for linear_regression, including edge cases.
# 1. Varying lengths: Generate lists of different lengths to test handling of different input sizes.
# 2. Constant x values: Include cases with constant x values to ensure StatisticsError is raised.
# 3. Proportional and non-proportional: Test both proportional and non-proportional cases.
# 4. Floating-point and integer data: Use floats to cover a wider range of possible input values.

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate lists of random floats with varying lengths
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=len(x)))

    # Introduce a chance of creating a list with constant x values
    if data.draw(st.booleans()):
        x = [x[0]] * len(x)

    # Choose whether to test the proportional case
    proportional = data.draw(st.booleans())

    # Check for StatisticsError when x is constant
    if all(v == x[0] for v in x):
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(x, y, proportional=proportional)
    else:
        # When x is not constant, ensure the function returns a tuple of two floats
        result = statistics.linear_regression(x, y, proportional=proportional)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(v, float) for v in result)

        # In the proportional case, check that the intercept is close to zero
        if proportional:
            slope, intercept = result
            assert math.isclose(intercept, 0.0, abs_tol=1e-10)
# End program