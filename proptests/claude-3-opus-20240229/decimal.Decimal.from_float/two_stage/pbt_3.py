from hypothesis import given, strategies as st
import decimal
import math

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_output_type(f):
    assert isinstance(decimal.Decimal.from_float(f), decimal.Decimal)

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_exact_representation(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal(str(f))

@given(st.sampled_from([float('inf'), float('-inf')]))
def test_decimal_from_float_infinity(f):
    if f == float('inf'):
        assert decimal.Decimal.from_float(f) == decimal.Decimal('Infinity')
    else:
        assert decimal.Decimal.from_float(f) == decimal.Decimal('-Infinity')

@given(st.floats(allow_nan=True, allow_infinity=False))
def test_decimal_from_float_nan(f):
    if math.isnan(f):
        assert math.isnan(decimal.Decimal.from_float(f))

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_from_float_equality(f):
    assert decimal.Decimal.from_float(f) == decimal.Decimal(f)
# End program