from hypothesis import given, strategies as st
from decimal import Decimal
from math import gcd
import pytest

# Summary: Generate Decimals from explicit edge-case strings plus constructed
# finite Decimal tuples with random signs, digit sequences, and exponents.
# This covers ordinary finite values, zeros including negative zero, large and
# small powers of ten, values requiring denominator reduction, infinities, quiet
# NaNs, and signaling NaNs. For finite Decimals, check that as_integer_ratio()
# returns integers in lowest terms with a positive denominator and exactly
# represents the Decimal. For infinities and NaNs, check the documented errors.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    finite_from_tuple = st.builds(
        lambda sign, digits, exponent: Decimal((sign, tuple(digits), exponent)),
        st.integers(min_value=0, max_value=1),
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=35),
        st.integers(min_value=-35, max_value=35),
    )

    edge_cases = st.sampled_from(
        [
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("-1"),
            Decimal("0.1"),
            Decimal("-0.1"),
            Decimal("3.14"),
            Decimal("-3.14"),
            Decimal("1E-35"),
            Decimal("-1E-35"),
            Decimal("1E+35"),
            Decimal("-1E+35"),
            Decimal("99999999999999999999999999999999999E-35"),
            Decimal("-99999999999999999999999999999999999E-35"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("NaN"),
            Decimal("-NaN"),
            Decimal("sNaN"),
            Decimal("-sNaN"),
        ]
    )

    x = data.draw(st.one_of(finite_from_tuple, edge_cases))

    if x.is_infinite():
        with pytest.raises(OverflowError):
            x.as_integer_ratio()
        return

    if x.is_nan():
        with pytest.raises(ValueError):
            x.as_integer_ratio()
        return

    n, d = x.as_integer_ratio()

    assert isinstance(n, int)
    assert isinstance(d, int)
    assert d > 0
    assert gcd(abs(n), d) == 1

    sign, digits, exponent = x.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit

    if sign:
        coefficient = -coefficient

    if exponent >= 0:
        expected_n = coefficient * (10 ** exponent)
        expected_d = 1
    else:
        expected_n = coefficient
        expected_d = 10 ** (-exponent)
        common = gcd(abs(expected_n), expected_d)
        expected_n //= common
        expected_d //= common

    assert (n, d) == (expected_n, expected_d)

# End program