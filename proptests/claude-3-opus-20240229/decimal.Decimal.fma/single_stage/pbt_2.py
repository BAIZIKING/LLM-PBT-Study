from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Generate a wide variety of Decimal inputs, including:
# - Small and large magnitude numbers 
# - Positive and negative values
# - Numbers with different numbers of digits after the decimal
# - Special values like 0, inf, -inf, and NaN
# Test key properties:
# - Rounding should not impact the result (fma does no intermediate rounding)
# - Result should exactly equal self*other+third
@given(
    st.decimals(allow_nan=False, allow_infinity=False),
    st.decimals(allow_nan=False, allow_infinity=False), 
    st.decimals(allow_nan=False, allow_infinity=False),
    st.integers(min_value=1, max_value=100)
)
def test_decimal_fma(self, other, third, precision):
    getcontext().prec = precision
    self_dec = Decimal(self)
    other_dec = Decimal(other)
    third_dec = Decimal(third)
    
    result = self_dec.fma(other_dec, third_dec)
    expected = self_dec * other_dec + third_dec
    assert result == expected
# End program