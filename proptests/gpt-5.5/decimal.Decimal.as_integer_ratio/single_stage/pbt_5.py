from hypothesis import given, strategies as st
from decimal import Decimal
from fractions import Fraction
from math import gcd
import pytest

# Summary: Generate finite Decimals from explicit sign/digits/exponent tuples to cover zero, negative zero, trailing/leading zeros, large coefficients, and varied positive/negative exponents; also generate infinities and NaNs. For finite values, check that the result is two ints, the denominator is positive, the fraction is in lowest terms, and it exactly equals an independently computed Fraction. For infinities and NaNs, check the documented exceptions.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    finite_decimals = st.builds(
        lambda sign, digits, exponent: Decimal((sign, digits, exponent)),
        st.integers(min_value=0, max_value=1),
        st.one_of(
            st.just((0,)),
            st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=40)
            .filter(lambda ds: any(ds))
            .map(tuple),
        ),
        st.integers(min_value=-80, max_value=80),
    )

    special_decimals = st.sampled_from(
        [
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("NaN"),
            Decimal("-NaN"),
            Decimal("sNaN"),
            Decimal("-sNaN"),
        ]
    )

    x = data.draw(st.one_of(finite_decimals, special_decimals))

    if x.is_infinite():
        with pytest.raises(OverflowError):
            x.as_integer_ratio()
        return

    if x.is_nan():
        with pytest.raises(ValueError):
            x.as_integer_ratio()
        return

    n, d = x.as_integer_ratio()

    assert type(n) is int
    assert type(d) is int
    assert d > 0
    assert gcd(abs(n), d) == 1

    sign, digits, exponent = x.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    if sign:
        coefficient = -coefficient

    if exponent >= 0:
        expected = Fraction(coefficient * (10**exponent), 1)
    else:
        expected = Fraction(coefficient, 10 ** (-exponent))

    assert Fraction(n, d) == expected
# End program