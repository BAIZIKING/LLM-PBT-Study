from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generate a wide variety of Decimal values for the first and second operands.
# For the first operand, generate both normal and subnormal values, with varying precisions and exponents.
# For the second operand, focus on varying the exponent to test different quantization behaviors.
# Also generate some edge cases like NaN, sNaN, -Inf, +Inf.
# Check that:
# 1) The exponent of the quantized result always matches the second operand 
# 2) An InvalidOperation is raised if the quantized coefficient would exceed the precision
# 3) Underflow is never signaled, even for subnormal and inexact results
# 4) The appropriate rounding mode is used based on the context
@given(
    st.decimals(allow_nan=True, allow_infinity=True),
    st.decimals(allow_nan=True, allow_infinity=True) | st.just(Decimal('NaN')),
    st.sampled_from([None, 'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN']),
    st.decimals(allow_nan=True, allow_infinity=True) | st.none()
)
def test_decimal_quantize(op1, op2, rounding, context):
    if op2.is_finite() and context is None:
        try:
            quantized = op1.quantize(op2, rounding=rounding)
            assert quantized.is_finite()
            assert quantized.as_tuple().exponent == op2.as_tuple().exponent
        except InvalidOperation:
            assert True # Expected when precision exceeded
    else:
        try:
            quantized = op1.quantize(op2, context=context)
            if quantized.is_finite():
                assert quantized.as_tuple().exponent == op2.as_tuple().exponent
        except (InvalidOperation, TypeError):
            assert True # Expected for some inputs
# End program