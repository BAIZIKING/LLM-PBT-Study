from hypothesis import given, strategies as st

# Summary: Draw homogeneous numeric inputs across int, finite float, Fraction, and Decimal values; include empty and singleton lists to check error behavior, plus zeros, negatives, duplicates, and varied lengths. For valid data, check documented properties: sample variance requires at least two values, is non-negative, is unchanged when xbar is omitted/None/the true mean, matches the sum-of-squared-deviations formula for an arbitrary xbar, is translation-invariant, and scales quadratically.
@given(st.data())
def test_statistics_variance(data):
    import math
    import pytest
    from decimal import Decimal
    from fractions import Fraction
    from statistics import StatisticsError, mean, variance

    def assert_close_or_equal(actual, expected):
        if isinstance(actual, Decimal) or isinstance(expected, Decimal):
            tolerance = Decimal("1e-20") * max(Decimal(1), abs(actual), abs(expected))
            assert abs(actual - expected) <= tolerance
        elif isinstance(actual, float) or isinstance(expected, float):
            assert math.isclose(
                float(actual),
                float(expected),
                rel_tol=1e-7,
                abs_tol=1e-7,
            )
        else:
            assert actual == expected

    numeric_kind = data.draw(st.sampled_from(["int", "float", "fraction", "decimal"]))

    if numeric_kind == "int":
        value_strategy = st.integers(min_value=-1_000_000, max_value=1_000_000)
    elif numeric_kind == "float":
        value_strategy = st.one_of(
            st.just(0.0),
            st.just(-0.0),
            st.floats(
                min_value=-1_000_000,
                max_value=1_000_000,
                allow_nan=False,
                allow_infinity=False,
                width=64,
            ),
        )
    elif numeric_kind == "fraction":
        value_strategy = st.one_of(
            st.just(Fraction(0, 1)),
            st.fractions(
                min_value=Fraction(-1_000_000, 1),
                max_value=Fraction(1_000_000, 1),
                max_denominator=1000,
            ),
        )
    else:
        value_strategy = st.one_of(
            st.just(Decimal("0")),
            st.decimals(
                min_value=Decimal("-1000000"),
                max_value=Decimal("1000000"),
                places=3,
                allow_nan=False,
                allow_infinity=False,
            ),
        )

    values = data.draw(st.lists(value_strategy, min_size=0, max_size=20))

    if len(values) < 2:
        with pytest.raises(StatisticsError):
            variance(values)
        with pytest.raises(StatisticsError):
            variance(values, None)
        with pytest.raises(StatisticsError):
            variance(values, data.draw(value_strategy))
        return

    n = len(values)
    actual = variance(values)
    actual_mean = mean(values)

    assert actual >= 0

    assert_close_or_equal(variance(values, None), actual)
    assert_close_or_equal(variance(values, actual_mean), actual)

    arbitrary_xbar = data.draw(value_strategy)
    expected_with_xbar = sum((x - arbitrary_xbar) ** 2 for x in values) / (n - 1)
    assert_close_or_equal(variance(values, arbitrary_xbar), expected_with_xbar)

    offset = data.draw(value_strategy)
    translated = [x + offset for x in values]
    assert_close_or_equal(variance(translated), actual)

    scale = data.draw(st.integers(min_value=-5, max_value=5))
    scaled = [x * scale for x in values]
    assert_close_or_equal(variance(scaled), actual * scale * scale)
# End program