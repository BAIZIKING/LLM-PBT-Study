from hypothesis import given, strategies as st
import decimal

@given(st.just(float('-inf')))
def test_decimal_from_float_negative_infinity_output(f):
    result = decimal.Decimal.from_float(f)
    assert result.is_infinite() and result.is_negative()
# End program