from hypothesis import given, strategies as st
import decimal

@given(
    st.decimals(allow_nan=False, allow_infinity=False),
    st.decimals(allow_nan=False, allow_infinity=False),
    st.decimals(allow_nan=False, allow_infinity=False),
    st.none() | st.builds(decimal.Context)
)
def test_decimal_fma_properties(self, other, third, context):
    if context is not None:
        decimal.setcontext(context)
    
    result = self.fma(other, third)
    expected = self * other + third
    
    assert result == expected
    assert isinstance(result, decimal.Decimal)
    assert result.is_finite() == expected.is_finite()
    assert result.is_signed() == expected.is_signed()
    assert result.as_tuple().exponent >= decimal.getcontext().prec
# End program