from hypothesis import given, strategies as st
from decimal import (Decimal, InvalidOperation, localcontext,
                     ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR,
                     ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN,
                     ROUND_05UP)

# Summary: Generate finite Decimals for the value, a Decimal whose exponent
# spans a wide range for the quantize template, and a rounding mode (or None).
# Verify that on success the result has the template's exponent and stays
# numerically close to the original (within one ulp), tolerating the
# documented InvalidOperation for out-of-range / too-precise results.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    # First operand: a finite decimal value to be quantized.
    value = data.draw(
        st.decimals(allow_nan=False, allow_infinity=False, places=None)
    )

    # Second operand: only its exponent matters. Build it from a chosen exponent.
    exp_value = data.draw(st.integers(min_value=-30, max_value=30))
    template = Decimal(1).scaleb(exp_value)  # e.g. 1E+5 or 1E-7

    # Rounding mode (or None to use context).
    rounding = data.draw(st.sampled_from([
        None, ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR,
        ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_05UP,
    ]))

    with localcontext() as ctx:
        ctx.prec = data.draw(st.integers(min_value=1, max_value=50))
        try:
            result = value.quantize(template, rounding=rounding)
        except InvalidOperation:
            # Documented error: coefficient too long, or exponent out of range.
            return

        # Property 1: result exponent equals the template's exponent.
        assert result.as_tuple().exponent == template.as_tuple().exponent

        # Property 2: result is numerically close to the original value.
        # The maximum change from rounding to the target exponent is one ulp.
        ulp = Decimal(1).scaleb(exp_value)
        # Use a generous context for the difference computation.
        with localcontext() as cmp_ctx:
            cmp_ctx.prec = 100
            diff = abs(value - result)
            assert diff <= ulp
# End program