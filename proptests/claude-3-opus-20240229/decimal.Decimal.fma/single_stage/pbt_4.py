from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Generate a wide variety of Decimal inputs, including:
# - Small and large positive values 
# - Small and large negative values
# - Values close to 0
# - Special values like NaN and infinity
# Also generate both positive and negative values for the third parameter.
# Use a context with high precision.
@given(st.decimals(allow_nan=True, allow_infinity=True), 
       st.decimals(allow_nan=True, allow_infinity=True),
       st.decimals(allow_nan=True, allow_infinity=True), 
       st.integers(min_value=1, max_value=100))
def test_decimal_fma(self, other, third, precision):
    getcontext().prec = precision
    
    # The result should equal self*other+third
    assert self.fma(other, third) == self*other + third
    
    # Changing rounding should not affect the result
    getcontext().rounding = ROUND_UP
    assert self.fma(other, third) == self*other + third
    getcontext().rounding = ROUND_DOWN 
    assert self.fma(other, third) == self*other + third

    # Should return NaN if any input is NaN
    nan = Decimal('NaN')
    assert nan.fma(other, third).is_nan()
    assert self.fma(nan, third).is_nan()
    assert self.fma(other, nan).is_nan()
# End program