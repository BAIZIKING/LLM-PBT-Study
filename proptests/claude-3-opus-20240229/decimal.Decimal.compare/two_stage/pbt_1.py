from hypothesis import given, strategies as st
import decimal

@given(st.decimals(), st.decimals())
def test_decimal_compare_returns_decimal(a, b):
    result = decimal.Decimal.compare(a, b)
    assert isinstance(result, decimal.Decimal)

@given(st.decimals(allow_nan=True))
def test_decimal_compare_nan_operand(a):
    nan = decimal.Decimal('NaN')
    result = decimal.Decimal.compare(a, nan)
    assert result.is_nan()
    result = decimal.Decimal.compare(nan, a)
    assert result.is_nan()

@given(st.decimals(allow_infinity=False), st.decimals(allow_infinity=False))
def test_decimal_compare_less_than(a, b):
    assume(a < b)
    result = decimal.Decimal.compare(a, b)
    assert result == decimal.Decimal('-1')

@given(st.decimals(allow_infinity=False))
def test_decimal_compare_equal(a):
    result = decimal.Decimal.compare(a, a)
    assert result == decimal.Decimal('0')

@given(st.decimals(allow_infinity=False), st.decimals(allow_infinity=False))
def test_decimal_compare_greater_than(a, b):
    assume(a > b)
    result = decimal.Decimal.compare(a, b)
    assert result == decimal.Decimal('1')
# End program