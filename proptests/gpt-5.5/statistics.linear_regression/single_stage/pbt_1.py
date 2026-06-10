from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate a mix of valid and invalid (x, y, proportional) inputs:
# mismatched lengths, too-short inputs, constant x, exact affine data, exact
# proportional data through the origin, and arbitrary small numeric data. Check
# documented errors for invalid inputs; for valid inputs, check tuple/named-field
# access, expected least-squares formulas, intercept behavior, and normal-equation
# residual properties.
@given(st.data())
def test_statistics_linear_regression(data):
    number = st.one_of(
        st.integers(-50, 50),
        st.floats(
            min_value=-50,
            max_value=50,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        ),
    )

    case = data.draw(
        st.sampled_from(
            [
                "invalid_mismatched_lengths",
                "invalid_too_short",
                "invalid_constant_x",
                "valid_exact_affine",
                "valid_exact_proportional",
                "valid_arbitrary_data",
            ]
        )
    )

    expect_error = False
    expected_slope = None
    expected_intercept = None

    if case == "invalid_mismatched_lengths":
        n = data.draw(st.integers(0, 6))
        m = data.draw(st.integers(0, 6).filter(lambda k: k != n))
        x = data.draw(st.lists(number, min_size=n, max_size=n))
        y = data.draw(st.lists(number, min_size=m, max_size=m))
        proportional = data.draw(st.booleans())
        expect_error = True

    elif case == "invalid_too_short":
        n = data.draw(st.integers(0, 1))
        x = data.draw(st.lists(number, min_size=n, max_size=n))
        y = data.draw(st.lists(number, min_size=n, max_size=n))
        proportional = data.draw(st.booleans())
        expect_error = True

    elif case == "invalid_constant_x":
        n = data.draw(st.integers(2, 8))
        c = data.draw(number)
        x = [c] * n
        y = data.draw(st.lists(number, min_size=n, max_size=n))
        proportional = False
        expect_error = True

    elif case == "valid_exact_affine":
        n = data.draw(st.integers(2, 8))
        x = data.draw(
            st.lists(number, min_size=n, max_size=n).filter(
                lambda xs: len(set(xs)) > 1
            )
        )
        expected_slope = data.draw(st.integers(-20, 20))
        expected_intercept = data.draw(st.integers(-20, 20))
        y = [expected_slope * xi + expected_intercept for xi in x]
        proportional = False

    elif case == "valid_exact_proportional":
        n = data.draw(st.integers(2, 8))
        x = data.draw(
            st.lists(number, min_size=n, max_size=n).filter(
                lambda xs: len(set(xs)) > 1 and any(xi != 0 for xi in xs)
            )
        )
        expected_slope = data.draw(st.integers(-20, 20))
        expected_intercept = 0.0
        y = [expected_slope * xi for xi in x]
        proportional = True

    else:
        n = data.draw(st.integers(2, 8))
        x = data.draw(
            st.lists(number, min_size=n, max_size=n).filter(
                lambda xs: len(set(xs)) > 1
            )
        )
        y = data.draw(st.lists(number, min_size=n, max_size=n))
        proportional = data.draw(st.booleans())

        if proportional:
            denominator = sum(xi * xi for xi in x)
            expected_slope = sum(xi * yi for xi, yi in zip(x, y)) / denominator
            expected_intercept = 0.0
        else:
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            denominator = sum((xi - x_mean) ** 2 for xi in x)
            expected_slope = (
                sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
                / denominator
            )
            expected_intercept = y_mean - expected_slope * x_mean

    if expect_error:
        try:
            statistics.linear_regression(x, y, proportional=proportional)
        except statistics.StatisticsError:
            return
        assert False, "linear_regression should reject invalid documented inputs"

    result = statistics.linear_regression(x, y, proportional=proportional)
    slope, intercept = result

    assert slope == result.slope
    assert intercept == result.intercept

    assert math.isclose(
        slope,
        expected_slope,
        rel_tol=1e-7,
        abs_tol=1e-7,
    )
    assert math.isclose(
        intercept,
        expected_intercept,
        rel_tol=1e-7,
        abs_tol=1e-7,
    )

    residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]

    if proportional:
        assert intercept == 0.0
        assert math.isclose(
            sum(xi * ri for xi, ri in zip(x, residuals)),
            0.0,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
    else:
        x_mean = sum(x) / len(x)
        assert math.isclose(
            sum(residuals),
            0.0,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            sum((xi - x_mean) * ri for xi, ri in zip(x, residuals)),
            0.0,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
# End program