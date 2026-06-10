from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: This test generates random Decimal objects for self, other, and third, including edge cases like zeros, infinities, and negative values. 
# It then checks if the result of fma matches the expected result of (self*other)+third calculated without intermediate rounding.
@given(st.decimals(allow_nan=False, allow_infinity=True), 
       st.decimals(allow_nan=False, allow_infinity=True),
       st.decimals(allow_nan=False, allow_infinity=True))
def test_decimal_Decimal_fma(self, other, third):
    expected_result = (self * other) + third  # Calculate expected result without fma
    actual_result = self.fma(other, third)  # Calculate result using fma
    assert actual_result == expected_result 
# End program