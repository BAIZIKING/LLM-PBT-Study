from hypothesis import given, strategies as st
from statistics import linear_regression

# Generate a variety of test cases, including:
# - Small and large x, y lists 
# - Negative and positive values
# - x values that are nearly constant to check for tolerance to small variance
# - Direct proportionality between x and y (for proportional=True)
# - Check for exception when x and y are different lengths or x has < 2 elements
@given(st.data())
def test_linear_regression(data):
    n = data.draw(st.integers(min_value=2, max_value=100))
    x = data.draw(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=n, max_size=n))
    noise = data.draw(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=n, max_size=n))
    slope = data.draw(st.floats(allow_infinity=False, allow_nan=False))
    intercept = data.draw(st.floats(allow_infinity=False, allow_nan=False))
    y = [slope * xi + intercept + noisei for xi, noisei in zip(x, noise)]

    # Check that output slope and intercept generate predicted y values close to actual
    slope_out, intercept_out = linear_regression(x, y)
    y_pred = [slope_out * xi + intercept_out for xi in x]
    assert max(abs(yi - yi_pred) for yi, yi_pred in zip(y, y_pred)) < 1e-6

    # Check proportional=True case
    if data.draw(st.booleans()):
        y = [slope * xi + noisei for xi, noisei in zip(x, noise)]
        slope_out, intercept_out = linear_regression(x, y, proportional=True)
        assert abs(intercept_out) < 1e-6  # intercept should be close to 0
        y_pred = [slope_out * xi for xi in x]
        assert max(abs(yi - yi_pred) for yi, yi_pred in zip(y, y_pred)) < 1e-6

    # Check validation
    with pytest.raises(StatisticsError):
        linear_regression(x[:1], y[:1])  # not enough x values
    with pytest.raises(StatisticsError): 
        linear_regression(x + [1], y)  # mismatched lengths
# End program