from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_property1(self, other, third):
    assert self.fma(other, third) == self * other + third

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_property2(self, other, third):
    assert isinstance(self.fma(other, third), decimal.Decimal)

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_property3(self, other, third):
    assert self.fma(other, third) == other.fma(self, third)

@given(st.integers(), st.integers(), st.integers())
def test_fma_property4(self, other, third):
    assert decimal.Decimal(self).fma(other, third) == decimal.Decimal(self * other + third)

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_property5(self, other, third, context):
    assert self.fma(other, third, context=context) == self.fma(other, third).quantize(decimal.Decimal('1'), rounding=context.rounding)
# End program