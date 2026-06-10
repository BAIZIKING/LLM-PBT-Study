from hypothesis import given, strategies as st
import decimal
import math


@st.composite
def finite_decimals(draw):
    # Keep coefficient size and exponent bounded to avoid enormous integers/overflows.
    sign = draw(st.integers(min_value=0, max_value=1))
    coefficient = draw(st.integers(min_value=0, max_value=10**80))
    exponent = draw(st.integers(min_value=-50, max_value=50))

    digits = tuple(int(ch) for ch in str(coefficient))
    return decimal.Decimal((sign, digits, exponent))


special_decimals = st.sampled_from(
    [
        decimal.Decimal("Infinity"),
        decimal.Decimal("-Infinity"),
        decimal.Decimal("NaN"),
        decimal.Decimal("-NaN"),
        decimal.Decimal("sNaN"),
        decimal.Decimal("-sNaN"),
    ]
)


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_integer_pair_property(data):
    x = data.draw(finite_decimals())
    n, d = x.as_integer_ratio()

    assert type(n) is int
    assert type(d) is int


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_positive_denominator_property(data):
    x = data.draw(finite_decimals())
    n, d = x.as_integer_ratio()

    assert d > 0


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_exact_value_property(data):
    x = data.draw(finite_decimals())
    n, d = x.as_integer_ratio()

    dec_tuple = x.as_tuple()
    coefficient = int("".join(str(digit) for digit in dec_tuple.digits))
    signed_coefficient = -coefficient if dec_tuple.sign else coefficient
    exponent = dec_tuple.exponent

    if exponent >= 0:
        expected_numerator = signed_coefficient * (10**exponent)
        expected_denominator = 1
    else:
        expected_numerator = signed_coefficient
        expected_denominator = 10 ** (-exponent)

    assert n * expected_denominator == expected_numerator * d


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_lowest_terms_property(data):
    x = data.draw(finite_decimals())
    n, d = x.as_integer_ratio()

    assert math.gcd(abs(n), d) == 1


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_special_values_raise_property(data):
    x = data.draw(special_decimals)

    if x.is_infinite():
        try:
            x.as_integer_ratio()
        except OverflowError:
            pass
        else:
            assert False
    else:
        assert x.is_nan()
        try:
            x.as_integer_ratio()
        except ValueError:
            pass
        else:
            assert False


# End program