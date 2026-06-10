from hypothesis import given, strategies as st
import decimal

@given(a=st.decimals(allow_nan=True), b=st.decimals(allow_nan=True))
def test_decimal_compare_nan_property(a, b):
    if decimal.Decimal(a).is_nan() or decimal.Decimal(b).is_nan():
        assert decimal.Decimal(a).compare(decimal.Decimal(b)).is_nan()

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False))
def test_decimal_compare_less_than_property(a, b):
    assume(a < b)
    assert decimal.Decimal(a).compare(decimal.Decimal(b)) == decimal.Decimal('-1')

@given(st.decimals(allow_nan=False))
def test_decimal_compare_equal_property(a):
    assert decimal.Decimal(a).compare(decimal.Decimal(a)) == decimal.Decimal('0')

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False))
def test_decimal_compare_greater_than_property(a, b):
    assume(a > b)
    assert decimal.Decimal(a).compare(decimal.Decimal(b)) == decimal.Decimal('1')

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_result_type_property(a, b):
    assert isinstance(decimal.Decimal(a).compare(decimal.Decimal(b)), decimal.Decimal)
# End program