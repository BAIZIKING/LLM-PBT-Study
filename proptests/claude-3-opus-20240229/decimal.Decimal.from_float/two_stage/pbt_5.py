from hypothesis import given, strategies as st
import decimal
import math

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_closest_representable(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal(f)

@given(st.just(float('inf')))
def test_decimal_from_float_positive_infinity(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal('Infinity')

@given(st.just(float('-inf')))
def test_decimal_from_float_negative_infinity(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal('-Infinity')

@given(st.just(float('nan')))
def test_decimal_from_float_nan(f):
    assert math.isnan(decimal.Decimal.from_float(f))

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_same_sign(f):
    decimal_value = decimal.Decimal.from_float(f)
    assert (f > 0 and decimal_value > 0) or (f < 0 and decimal_value < 0) or (f == 0 and decimal_value == 0)
# End program