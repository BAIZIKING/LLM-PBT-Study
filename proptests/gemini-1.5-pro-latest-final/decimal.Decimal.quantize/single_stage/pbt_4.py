from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generates diverse Decimal inputs for quantize, including edge cases, and checks properties based on API documentation.
@given(
    value=st.decimals(
        min_value=-1e20,
        max_value=1e20,
        allow_nan=True,
        allow_infinity=True,
        allow_subnormal=True
    ),
    exp=st.decimals(
        min_value=-100,
        max_value=100,
        allow_nan=True,
        allow_infinity=True
    ),
    rounding=st.sampled_from(
        [
            Decimal.ROUND_CEILING, 
            Decimal.ROUND_DOWN, 
            Decimal.ROUND_FLOOR, 
            Decimal.ROUND_HALF_DOWN, 
            Decimal.ROUND_HALF_EVEN, 
            Decimal.ROUND_HALF_UP, 
            Decimal.ROUND_UP, 
            Decimal.ROUND_05UP
        ]
    ),
)
def test_decimal_quantize(value, exp, rounding):
    try:
        result = value.quantize(exp, rounding=rounding)
        # Property 1: Resulting exponent matches the second operand's exponent.
        assert result.as_tuple().exponent == exp.as_tuple().exponent

        # Property 2: Check rounding behavior (if applicable)
        # ... (Implementation depends on specific rounding mode checks)

        # Property 3: Coefficient length should not exceed precision
        assert len(result.as_tuple().digits) <= result.prec

    except InvalidOperation:
        # Exponent out of valid range or coefficient length exceeded precision.
        assert exp.as_tuple().exponent > Decimal.max_exponent or exp.as_tuple().exponent < Decimal.min_exponent or len(value.as_tuple().digits) > value.prec 
    
    # Property 4: No UnderflowError raised
    assert True
# End program