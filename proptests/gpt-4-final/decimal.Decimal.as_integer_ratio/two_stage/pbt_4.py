from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_property_1(dec):
    ratio = dec.as_integer_ratio()
    assert isinstance(ratio, tuple) and len(ratio) == 2

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_property_2(dec):
    numerator, denominator = dec.as_integer_ratio()
    assert isinstance(numerator, int) and isinstance(denominator, int)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_property_3(dec):
    _, denominator = dec.as_integer_ratio()
    assert denominator > 0

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_property_4(dec):
    numerator, denominator = dec.as_integer_ratio()
    assert decimal.Decimal(numerator) / decimal.Decimal(denominator) == dec

@given(st.integers())
def test_as_integer_ratio_property_5(intgr):
    dec = decimal.Decimal(intgr)
    _, denominator = dec.as_integer_ratio()
    assert denominator == 1