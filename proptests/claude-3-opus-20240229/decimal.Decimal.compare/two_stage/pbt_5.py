from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_nan(a, b):
    if a.is_nan() or b.is_nan():
        assert decimal.Decimal.compare(a, b).is_nan()

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False).filter(lambda x: x > 0))
def test_decimal_compare_less_than(a, b):
    assert decimal.Decimal.compare(a, a + b) == decimal.Decimal('-1')

@given(st.decimals(allow_nan=False))
def test_decimal_compare_equal(a):
    assert decimal.Decimal.compare(a, a) == decimal.Decimal('0')

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False).filter(lambda x: x > 0))
def test_decimal_compare_greater_than(a, b):
    assert decimal.Decimal.compare(a + b, a) == decimal.Decimal('1')

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_returns_decimal(a, b):
    assert isinstance(decimal.Decimal.compare(a, b), decimal.Decimal)
# End program