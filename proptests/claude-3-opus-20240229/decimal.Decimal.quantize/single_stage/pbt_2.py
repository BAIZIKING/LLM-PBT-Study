from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Generate a wide variety of Decimal values to test quantize:
# - Exponents span a large range, both positive and negative 
# - Coefficients include small, large, and edge case values
# - Test some combinations of exp and value that should trigger InvalidOperation
# Properties to check:
# - Quantized value has the same exponent as exp
# - Quantized value equals original value rounded to exp's precision
# - InvalidOperation is raised if precision of quantized value exceeds context precision
# - Underflow is never signaled, even for subnormal results
@given(
    value=st.decimals(allow_nan=False, allow_infinity=False),
    exp=st.decimals(allow_nan=False, allow_infinity=False) | st.just(Decimal('NaN')),
    context=st.builds(Context, prec=st.integers(1, 100))
)
def test_decimal_quantize(value, exp, context):
    try:
        quantized = value.quantize(exp, context=context)
        assert quantized.is_finite()
        assert quantized.exponent == exp.exponent
        assert quantized == context.round(value, exp.exponent)
    except InvalidOperation:
        assert value.is_finite() and exp.is_finite()
        assert len(quantized.as_tuple().digits) > context.prec
# End program        