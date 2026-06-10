from hypothesis import given, strategies as st
import statistics
import math

_SMALL_INTS = st.integers(min_value=-1_000, max_value=1_000)
_MEDIUM_INTS = st.integers(min_value=-10_000, max_value=10_000)


@st.composite
def regression_data(draw):
    n = draw(st.integers(min_value=2, max_value=20))
    x = draw(st.lists(_SMALL_INTS, min_size=n, max_size=n, unique=True))
    y = draw(st.lists(_MEDIUM_INTS, min_size=n, max_size=n))
    return x, y


@st.composite
def exact_linear_data(draw):
    n = draw(st.integers(min_value=2, max_value=20))
    x = draw(st.lists(_SMALL_INTS, min_size=n, max_size=n, unique=True))
    expected_slope = draw(st.integers(min_value=-1_000, max_value=1_000))
    expected_intercept = draw(st.integers(min_value=-10_000, max_value=10_000))
    y = [expected_slope * xi + expected_intercept for xi in x]
    return x, y, expected_slope, expected_intercept


@st.composite
def exact_proportional_data(draw):
    n = draw(st.integers(min_value=2, max_value=20))
    x = draw(st.lists(_SMALL_INTS, min_size=n, max_size=n, unique=True))
    expected_slope = draw(st.integers(min_value=-1_000, max_value=1_000))
    y = [expected_slope * xi for xi in x]
    return x, y, expected_slope


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)


@given(st.data())
def test_statistics_linear_regression_property_1(data):
    x, y = data.draw(regression_data())

    model = statistics.linear_regression(x, y)

    mean_y = statistics.fmean(y)
    fitted_at_mean_x = model.slope * statistics.fmean(x) + model.intercept

    assert close(mean_y, fitted_at_mean_x)


@given(st.data())
def test_statistics_linear_regression_property_2(data):
    x, y = data.draw(regression_data())

    model = statistics.linear_regression(x, y, proportional=True)

    assert model.intercept == 0.0


@given(st.data())
def test_statistics_linear_regression_property_3(data):
    x, y, expected_slope, expected_intercept = data.draw(exact_linear_data())

    model = statistics.linear_regression(x, y)

    assert close(model.slope, expected_slope)
    assert close(model.intercept, expected_intercept)


@given(st.data())
def test_statistics_linear_regression_property_4(data):
    x, y, expected_slope = data.draw(exact_proportional_data())

    model = statistics.linear_regression(x, y, proportional=True)

    assert close(model.slope, expected_slope)
    assert model.intercept == 0.0


@given(st.data())
def test_statistics_linear_regression_property_5(data):
    x, y = data.draw(regression_data())

    model = statistics.linear_regression(x, y)
    residuals = [yi - (model.slope * xi + model.intercept) for xi, yi in zip(x, y)]

    residual_sum = math.fsum(residuals)
    x_residual_sum = math.fsum(xi * ri for xi, ri in zip(x, residuals))

    residual_scale = max(
        1.0,
        math.fsum(abs(yi) + abs(model.slope * xi) + abs(model.intercept)
                  for xi, yi in zip(x, y)),
    )
    x_residual_scale = max(
        1.0,
        math.fsum(abs(xi * yi) + abs(model.slope * xi * xi) + abs(model.intercept * xi)
                  for xi, yi in zip(x, y)),
    )

    assert abs(residual_sum) <= 1e-6 * residual_scale
    assert abs(x_residual_sum) <= 1e-6 * x_residual_scale

    proportional_model = statistics.linear_regression(x, y, proportional=True)
    proportional_residuals = [
        yi - proportional_model.slope * xi for xi, yi in zip(x, y)
    ]

    proportional_x_residual_sum = math.fsum(
        xi * ri for xi, ri in zip(x, proportional_residuals)
    )
    proportional_x_residual_scale = max(
        1.0,
        math.fsum(abs(xi * yi) + abs(proportional_model.slope * xi * xi)
                  for xi, yi in zip(x, y)),
    )

    assert abs(proportional_x_residual_sum) <= 1e-6 * proportional_x_residual_scale
# End program