from hypothesis import given, strategies as st
import statistics
import math


def _assert_close(actual, expected, *, rel_tol=1e-10, abs_tol=1e-10):
    assert math.isclose(float(actual), float(expected), rel_tol=rel_tol, abs_tol=abs_tol)


@given(st.data())
def test_statistics_linear_regression_intercept_matches_means(data):
    n = data.draw(st.integers(min_value=2, max_value=20))
    x = data.draw(
        st.lists(
            st.integers(min_value=-1_000, max_value=1_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    y = data.draw(
        st.lists(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            min_size=n,
            max_size=n,
        )
    )

    model = statistics.linear_regression(x, y)
    expected_intercept = statistics.fmean(y) - model.slope * statistics.fmean(x)

    _assert_close(model.intercept, expected_intercept)


@given(st.data())
def test_statistics_linear_regression_line_passes_through_centroid(data):
    n = data.draw(st.integers(min_value=2, max_value=20))
    x = data.draw(
        st.lists(
            st.integers(min_value=-1_000, max_value=1_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    y = data.draw(
        st.lists(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            min_size=n,
            max_size=n,
        )
    )

    model = statistics.linear_regression(x, y)
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)

    _assert_close(mean_y, model.slope * mean_x + model.intercept)


@given(st.data())
def test_statistics_linear_regression_proportional_intercept_is_zero(data):
    n = data.draw(st.integers(min_value=2, max_value=20))
    x = data.draw(
        st.lists(
            st.integers(min_value=-1_000, max_value=1_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    y = data.draw(
        st.lists(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            min_size=n,
            max_size=n,
        )
    )

    model = statistics.linear_regression(x, y, proportional=True)

    assert model.intercept == 0.0


@given(st.data())
def test_statistics_linear_regression_proportional_slope_formula(data):
    n = data.draw(st.integers(min_value=2, max_value=20))
    x = data.draw(
        st.lists(
            st.integers(min_value=-1_000, max_value=1_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    y = data.draw(
        st.lists(
            st.integers(min_value=-1_000_000, max_value=1_000_000),
            min_size=n,
            max_size=n,
        )
    )

    model = statistics.linear_regression(x, y, proportional=True)
    expected_slope = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)

    _assert_close(model.slope, expected_slope)


@given(st.data())
def test_statistics_linear_regression_recovers_exact_linear_relationship(data):
    n = data.draw(st.integers(min_value=2, max_value=20))
    x = data.draw(
        st.lists(
            st.integers(min_value=-1_000, max_value=1_000),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    slope = data.draw(st.integers(min_value=-10_000, max_value=10_000))
    intercept = data.draw(st.integers(min_value=-10_000, max_value=10_000))
    y = [slope * xi + intercept for xi in x]

    model = statistics.linear_regression(x, y)
    proportional_model = statistics.linear_regression(
        x,
        [slope * xi for xi in x],
        proportional=True,
    )

    _assert_close(model.slope, slope)
    _assert_close(model.intercept, intercept)
    _assert_close(proportional_model.slope, slope)
    assert proportional_model.intercept == 0.0


# End program