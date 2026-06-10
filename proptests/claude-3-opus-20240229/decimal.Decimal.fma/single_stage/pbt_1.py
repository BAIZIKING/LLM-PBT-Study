from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Summary: 
# Generate a wide range of Decimal inputs, including:
# - Small and large magnitudes
# - Positive and negative values 
# - Integer-like and fractional values
# - Special values like 0, inf, nan
# Properties to test:
# - Result should equal self*other+third
# - No intermediate rounding of self*other
# - Respects precision of current context 
@given(
    st.decimals(allow_nan=True, allow_infinity=True), 
    st.decimals(allow_nan=True, allow_infinity=True),
    st.decimals(allow_nan=True, allow_infinity=True), 
    st.integers(min_value=1, max_value=100)
)
def test_decimal_fma(self, other, third, precision):
    getcontext().prec = precision
    
    result = self.fma(other, third)
    expected = self * other + third

    assert result == expected
    assert result.as_tuple().exponent >= min(
        self.as_tuple().exponent + other.as_tuple().exponent,
        expected.as_tuple().exponent
    )
# End program