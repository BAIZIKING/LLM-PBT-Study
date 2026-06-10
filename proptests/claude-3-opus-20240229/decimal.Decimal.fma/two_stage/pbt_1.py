from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), 
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_accuracy(self, other, third):
    assert self.fma(other, third) == self * other + third

@given(st.decimals(allow_nan=False, allow_infinity=False), 
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_sign(self, other, third):
    assert (self.fma(other, third)).sign() == (self * other + third).sign()
    
@given(st.decimals(allow_nan=False, allow_infinity=False), 
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_precision(self, other, third):
    assert self.fma(other, third).precision() <= max(self.precision(), other.precision(), third.precision())
    
@given(st.decimals(allow_nan=False, allow_infinity=False), 
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_finite(self, other, third):
    assert self.fma(other, third).is_finite()
    
@given(st.decimals(allow_nan=False, allow_infinity=False), 
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_fma_associative(self, other, third, fourth, fifth):
    assert (self.fma(other, third)).fma(fourth, fifth) == self.fma(other.fma(third, fourth), fifth)
# End program