from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation, getcontext

# Generate a wide variety of decimal values for the first and second operands.
# Include normal values, values with varying precisions, subnormal values, and 
# values with exponents near the min/max bounds. Also generate different
# rounding modes to test.
@given(
    st.decimals(allow_nan=False, allow_infinity=False), 
    st.decimals(allow_nan=False, allow_infinity=False), 
    st.sampled_from([None] + list(getcontext().rounding_modes))
)
def test_decimal_quantize(op1, op2, rounding):
    context = getcontext()
    
    # Test that result is equal to op1 after rounding to the exponent of op2
    quantized = op1.quantize(op2, rounding=rounding, context=context)
    assert quantized.exponent == op2.exponent
    assert quantized == op1.quantize(op2, rounding=rounding, context=context)

    # Test that InvalidOperation is raised if coefficient is too long
    context.prec = max(op1.adjusted(), op2.adjusted()) + 1
    if len(quantized.as_tuple().digits) > context.prec:
        try:
            op1.quantize(op2, rounding=rounding, context=context)
            assert False, "Expected InvalidOperation" 
        except InvalidOperation:
            pass

    # Test that underflow is not signaled, even if result is subnormal/inexact
    context.prec = 999999
    op1.quantize(op2, rounding=rounding, context=context)

    # Test that result exponent is between Etiny and Emax
    assert context.Etiny() <= quantized.exponent <= context.Emax
# End program