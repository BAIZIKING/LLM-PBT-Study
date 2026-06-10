from hypothesis import given, strategies as st
import decimal
import math

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_output_type(f):
    assert isinstance(decimal.Decimal.from_float(f), decimal.Decimal)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_equivalence(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal(str(f))

@given(st.just(float('nan')))
def test_decimal_from_float_nan(f):
    assert decimal.Decimal.from_float(f).is_nan()

@given(st.just(float('inf')))
def test_decimal_from_float_infinity(f):
    assert decimal.Decimal.from_float(f).is_infinite()

@given(st.just(float('-inf')))
def test_decimal_from_float_negative_infinity(f):
    d = decimal.Decimal.from_float(f)
    assert d.is_infinite() and d.is_signed()
# End program