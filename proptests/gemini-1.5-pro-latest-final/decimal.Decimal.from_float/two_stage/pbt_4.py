from hypothesis import given, strategies as st
import decimal

@given(st.floats(allow_nan=True, allow_infinity=True))
def test_decimal_from_float_type(f):
    result = decimal.Decimal.from_float(f)
    assert isinstance(result, decimal.Decimal)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_decimal_point(f):
    result = str(decimal.Decimal.from_float(f))
    assert '.' in result

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_finite(f):
    result = decimal.Decimal.from_float(f)
    assert result.is_finite()

@given(st.floats(allow_nan=True, allow_infinity=False, nan_strategy=st.just(float('nan'))))
def test_decimal_from_float_nan(f):
    result = decimal.Decimal.from_float(f)
    assert result.is_nan()

@given(st.floats(allow_nan=False, allow_infinity=True))
def test_decimal_from_float_infinity(f):
    result = decimal.Decimal.from_float(f)
    assert result.is_infinite()
# End program