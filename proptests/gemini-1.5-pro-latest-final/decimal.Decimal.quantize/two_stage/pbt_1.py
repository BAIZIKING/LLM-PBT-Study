from hypothesis import given, strategies as st
import decimal

# Define strategies for Decimal generation while avoiding overflows
max_exponent = decimal.Decimal.max_exponent()
min_exponent = decimal.Decimal.min_exponent()
safe_exponents = st.integers(min_value=min_exponent, max_value=max_exponent)

@given(
    st.decimals(allow_infinity=False, allow_nan=False), 
    st.decimals(allow_infinity=False, allow_nan=False, exponent=safe_exponents) 
)
@settings(max_examples=1000, deadline=None)  # Increase examples for thorough testing
def test_decimal_quantize_no_underflow(num, exp):
    quantized = num.quantize(exp)
    assert not quantized.is_subnormal() or not quantized.is_inexact()
# End program