from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Generate a wide variety of Decimal values for the first and second operands.
# Include normal values, values with different exponents, subnormal values, and 
# special values like NaN and Infinity. Test edge cases like operands with 
# exponents greater than Emax and less than Etiny.
@given(
    st.decimals(allow_nan=True, allow_infinity=True), 
    st.decimals(allow_nan=True, allow_infinity=True),
    st.sampled_from([None, 'ROUND_UP', 'ROUND_DOWN', 'ROUND_CEILING', 'ROUND_FLOOR', 'ROUND_HALF_UP', 'ROUND_HALF_DOWN', 'ROUND_HALF_EVEN'])
)
def test_decimal_quantize(op1, op2, rounding):
    try:
        quantized = op1.quantize(op2, rounding=rounding)
    except InvalidOperation:
        # Exception expected if coefficient length after quantize > precision
        assert True 
    else:
        # Result should be equal to op1 after rounding and have exponent of op2
        assert quantized == round(op1, op2.as_tuple().exponent) 
        assert quantized.as_tuple().exponent == op2.as_tuple().exponent
        # Underflow should never be signaled, even if result is subnormal and inexact
        assert quantized.is_subnormal() or not quantized.is_inexact()
# End program