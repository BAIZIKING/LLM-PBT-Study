from hypothesis import given, strategies as st
import decimal
import math


finite_decimals = st.decimals(
    min_value=decimal.Decimal("-1e50"),
    max_value=decimal.Decimal("1e50"),
    places=20,
    allow_nan=False,
    allow_infinity=False,
)


@given(finite_decimals)
def test_decimal_Decimal_as_integer_ratio_returns_integer_pair(x):
    result = x.as_integer_ratio()

    assert isinstance(result, tuple)
    assert len(result) == 2

    n, d = result
    assert isinstance(n, int)
    assert isinstance(d, int)


@given(finite_decimals)
def test_decimal_Decimal_as_integer_ratio_denominator_is_positive(x):
    n, d = x.as_integer_ratio()

    assert d > 0


@given(finite_decimals)
def test_decimal_Decimal_as_integer_ratio_is_in_lowest_terms(x):
    n, d = x.as_integer_ratio()

    assert math.gcd(abs(n), d) == 1


@given(finite_decimals)
def test_decimal_Decimal_as_integer_ratio_is_exact(x):
    n, d = x.as_integer_ratio()

    sign, digits, exponent = x.as_tuple()
    coefficient = int("".join(map(str, digits))) if digits else 0

    if sign:
        coefficient = -coefficient

    if exponent >= 0:
        expected_n = coefficient * (10 ** exponent)
        expected_d = 1
    else:
        expected_n = coefficient
        expected_d = 10 ** (-exponent)

    common_divisor = math.gcd(abs(expected_n), expected_d)
    expected_n //= common_divisor
    expected_d //= common_divisor

    assert (n, d) == (expected_n, expected_d)


@given(
    st.sampled_from(
        [
            decimal.Decimal("Infinity"),
            decimal.Decimal("-Infinity"),
            decimal.Decimal("NaN"),
            decimal.Decimal("-NaN"),
            decimal.Decimal("sNaN"),
            decimal.Decimal("-sNaN"),
        ]
    )
)
def test_decimal_Decimal_as_integer_ratio_rejects_non_finite_values(x):
    if x.is_infinite():
        expected_exception = OverflowError
    else:
        expected_exception = ValueError

    try:
        x.as_integer_ratio()
    except expected_exception:
        pass
    else:
        assert False, f"Expected {expected_exception.__name__}"


# End program