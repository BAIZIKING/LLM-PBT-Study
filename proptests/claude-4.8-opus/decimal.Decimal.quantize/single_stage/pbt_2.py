from hypothesis import given, strategies as st
from decimal import (
    Decimal, localcontext, InvalidOperation,
    ROUND_HALF_EVEN, ROUND_UP, ROUND_DOWN, ROUND_CEILING,
    ROUND_FLOOR, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_05UP,
)

# Summary: Generate finite decimals for both the value and the exp-provider operand
# (only its exponent matters), plus a rounding mode (or None). Check that the result's
# exponent equals the exp operand's exponent, and that the rounded result stays within
# one quantum of the original value. InvalidOperation (precision/Emax/Etiny) is tolerated.
@given(st.data())
def test_decimal_Decimal_quantize():
    data = st.data()

    finite_decimals = st.decimals(
        allow_nan=False, allow_infinity=False,
        min_value=Decimal("-1e10"), max_value=Decimal("1e10"),
    )

    value = data.draw(finite_decimals, label="value")
    exp_operand = data.draw(finite_decimals, label="exp_operand")
    rounding = data.draw(
        st.sampled_from([
            None,
            ROUND_HALF_EVEN, ROUND_UP, ROUND_DOWN, ROUND_CEILING,
            ROUND_FLOOR, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_05UP,
        ]),
        label="rounding",
    )

    with localcontext() as ctx:
        # Use a reasonably large precision to allow most quantize operations.
        ctx.prec = 50
        try:
            result = value.quantize(exp_operand, rounding=rounding)
        except InvalidOperation:
            # Documented: signaled if coefficient exceeds precision, or exponent
            # out of [Etiny, Emax]. This is an acceptable outcome.
            return

        # Property 1: result exponent equals the exp operand's exponent.
        target_exp = exp_operand.as_tuple().exponent
        assert result.as_tuple().exponent == target_exp, (
            f"Expected exponent {target_exp}, got {result.as_tuple().exponent}"
        )

        # Property 2: result is just a rounding of value, so the difference must be
        # less than one quantum (10**target_exp) in magnitude.
        quantum = Decimal(1).scaleb(target_exp)
        diff = abs(result - value)
        assert diff < quantum, (
            f"Rounded result {result} differs from {value} by {diff}, "
            f"which is not less than one quantum {quantum}"
        )
# End program