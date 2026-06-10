from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_equality(self, other, third):
    assert self.fma(other, third) == self * other + third

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_commutativity(self, other, third):
    assert self.fma(other, third) == self * other + third
    assert self.fma(third, other) == self * third + other

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_distributivity(self, other1, other2, third):
    assert self.fma(other1 + other2, third) == self.fma(other1, third) + self.fma(other2, third)

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_zero_handling(self, other, third):
    assert decimal.Decimal('0').fma(other, third) == other + third
    assert self.fma(decimal.Decimal('0'), third) == third
    assert self.fma(other, decimal.Decimal('0')) == self * other

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.builds(decimal.Context))
def test_fma_context_preservation(self, other, third, context):
    result = self.fma(other, third, context=context)
    assert result.context == context
# End program