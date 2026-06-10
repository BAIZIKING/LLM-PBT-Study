from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_nan(a, b):
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    if decimal.Decimal(a).is_nan() or decimal.Decimal(b).is_nan():
        assert result.is_nan()

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False))
def test_decimal_compare_less_than(a, b):
    assume(a < b)
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    assert result == decimal.Decimal('-1')

@given(st.decimals(allow_nan=False))
def test_decimal_compare_equal(a):
    result = decimal.Decimal(a).compare(decimal.Decimal(a))
    assert result == decimal.Decimal('0')

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False))
def test_decimal_compare_greater_than(a, b):
    assume(a > b)
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    assert result == decimal.Decimal('1')

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_returns_decimal(a, b):
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    assert isinstance(result, decimal.Decimal)
# End program