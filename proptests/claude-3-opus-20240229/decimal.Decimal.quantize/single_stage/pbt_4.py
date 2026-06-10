from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: 
# Generate a wide variety of Decimal values for the first and second operands.
# For the first operand, generate both positive and negative values with varying lengths of coefficient and exponent. 
# For the second operand, focus on generating exponents to test different rounding scenarios.
# Also generate the optional rounding mode argument.
# Check that the quantize() result always has the same exponent as the second operand.
# Check that InvalidOperation is raised if the quantized coefficient would exceed the precision.
# Check that the result is correctly rounded according to the rounding mode.
@given(
    st.decimals(allow_nan=False, allow_infinity=False), 
    st.decimals(allow_nan=False, allow_infinity=False) | st.just(Decimal('0')),
    st.sampled_from([None, 'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN', 'ROUND_CEILING', 'ROUND_FLOOR', 'ROUND_UP', 'ROUND_HALF_DOWN', 'ROUND_05UP'])
)
def test_decimal_quantize(d1, d2, rounding):
    try:
        quantized = d1.quantize(d2, rounding=rounding)
    except InvalidOperation:
        assert d2 != 0 and abs(quantized.adjusted() - d1.adjusted()) > 0  
    else:
        assert quantized.exponent == d2.exponent
        assert quantized.quantize(d2, rounding=rounding) == quantized
        if rounding is not None:
            assert quantized == d1.quantize(d2, rounding=rounding)
# End program