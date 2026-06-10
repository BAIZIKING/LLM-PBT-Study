from hypothesis import given, strategies as st
from math import gcd
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_tuple_of_integers(dec):
    n, d = dec.as_integer_ratio()
    assert isinstance(n, int) and isinstance(d, int)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_positive_denominator(dec):
    _, d = dec.as_integer_ratio()
    assert d > 0

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_fraction_in_lowest_terms(dec):
    n, d = dec.as_integer_ratio()
    assert gcd(n, d) == 1

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_fraction_equal_to_original_decimal(dec):
    n, d = dec.as_integer_ratio()
    assert decimal.Decimal(n) / decimal.Decimal(d) == dec

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_numerator_multiplied_by_decimal_to_power_of_denominator_is_integer(dec):
    n, d = dec.as_integer_ratio()
    assert (dec ** d) * n % 1 == 0
# End program