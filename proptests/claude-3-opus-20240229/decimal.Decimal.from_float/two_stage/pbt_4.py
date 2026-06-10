from hypothesis import given, strategies as st
import decimal
from math import isnan, isinf

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_returns_decimal(f):
    assert isinstance(decimal.Decimal.from_float(f), decimal.Decimal)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_equals_input(f):
    assert float(decimal.Decimal.from_float(f)) == f

@given(st.floats(allow_nan=True, allow_infinity=False))
def test_decimal_from_float_handles_nan(f):
    if isnan(f):
        assert decimal.Decimal.from_float(f).is_nan()
    else:
        assert not decimal.Decimal.from_float(f).is_nan()

@given(st.floats(allow_nan=False, allow_infinity=True))
def test_decimal_from_float_handles_infinity(f):
    if isinf(f) and f > 0:
        assert decimal.Decimal.from_float(f).is_infinite() and decimal.Decimal.from_float(f) > 0
    elif isinf(f) and f < 0:
        assert decimal.Decimal.from_float(f).is_infinite() and decimal.Decimal.from_float(f) < 0
    else:
        assert not decimal.Decimal.from_float(f).is_infinite()

@given(st.integers())
def test_decimal_from_float_handles_integers(i):
    assert decimal.Decimal.from_float(i) == decimal.Decimal(i)
# End program