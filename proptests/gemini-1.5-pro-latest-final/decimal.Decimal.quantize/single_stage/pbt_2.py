from hypothesis import given, strategies as st
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, Context

# Summary: Generates random Decimal operands, rounding modes, and contexts to test quantize behavior.
@given(
    operand1=st.decimals(
        min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
    ),
    operand2=st.decimals(
        min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
    ),
    rounding_mode=st.sampled_from(
        [ROUND_HALF_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR, ROUND_05UP]
    ),
    context=st.one_of(
        st.none(),
        st.builds(
            Context,
            prec=st.integers(min_value=1, max_value=100),
            rounding=st.sampled_from(
                [ROUND_HALF_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR, ROUND_05UP]
            ),
        ),
    ),
)
def test_decimal_quantize(operand1, operand2, rounding_mode, context):
    try:
        result = operand1.quantize(operand2, rounding=rounding_mode, context=context)
        assert result.as_tuple().exponent == operand2.as_tuple().exponent
        # Check precision limitation
        if len(str(abs(result)).split('.')[1]) > Context().prec:
            raise AssertionError("Result precision exceeds current context precision")
    except InvalidOperation:
        # Check if expected InvalidOperation due to precision limitation
        if len(str(abs(operand1)).split('.')[1]) > Context().prec:
            pass  # Expected error
        else:
            raise  # Unexpected error

# End program