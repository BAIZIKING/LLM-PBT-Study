from hypothesis import given, strategies as st
import numpy as np

# Summary: The generation strategy aims to create a wide variety of input scenarios for the statistics.linear_regression function, including both valid and edge cases. 
# It generates random arrays of x and y values, considering different lengths, value ranges, and potential for constant x values. 
# Additionally, it explores the 'proportional' parameter with True and False values to cover both simple and proportional linear regression cases.

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate random lengths for the input arrays, ensuring at least two elements
    length = data.draw(st.integers(min_value=2, max_value=100))

    # Generate x and y values as NumPy arrays
    x = data.draw(st.arrays(np.float64, shape=(length,), elements=st.floats(allow_nan=False, allow_infinity=False)))
    y = data.draw(st.arrays(np.float64, shape=(length,), elements=st.floats(allow_nan=False, allow_infinity=False)))

    # Introduce edge case: constant x values with a small probability
    if data.draw(st.booleans(p=0.1)):
        x = np.full_like(x, x[0])  # Make all x values the same

    # Explore both 'proportional' settings: True and False
    proportional = data.draw(st.booleans())

    # Attempt to compute linear regression and check properties based on documentation
    try:
        slope, intercept = statistics.linear_regression(x, y, proportional=proportional)

        # Check that the returned slope and intercept are numeric values
        assert isinstance(slope, float) and np.isfinite(slope)
        assert isinstance(intercept, float) and np.isfinite(intercept)

        # If 'proportional' is True, the intercept should be very close to zero
        if proportional:
            assert math.isclose(intercept, 0.0, abs_tol=1e-10)

        # Optionally, perform additional checks related to the regression model's fit 
        # (e.g., using R-squared or other metrics) depending on the desired level of testing.

    except statistics.StatisticsError as e:
        # Check for expected StatisticsError when x is constant
        if np.all(x == x[0]):
            assert str(e) == "x must not be constant"
        else:
            raise  # Unexpected error

# End program