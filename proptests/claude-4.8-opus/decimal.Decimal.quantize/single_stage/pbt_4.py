from hypothesis import given, strategies as st
from decimal import Decimal, Context, InvalidOperation, ROUND_HALF_EVEN, localcontext

# Summary: Generate a finite Decimal value as the first operand and a finite
# Decimal whose exponent serves as the quantization template. Use a context with
# generous precision. Verify that on success the result's exponent matches the
# template's exponent, the coefficient fits within precision, and the result is
# within one ULP of the original value; tolerate legitimate InvalidOperation.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    # First operand: a finite decimal value
    value = data.draw(
        st.decimals(allow_nan=False, allow_infinity=False, places=None),
        label="value",
    )
    # Second operand: a finite decimal; only its exponent matters.
    # Keep exponents in a moderate range to stay within Emax/Etiny often.
    exp_template = data.draw(
        st.decimals(allow_nan=False, allow_infinity=False, places=None),
        label="exp_template",
    )

    prec = data.draw(st.integers(min_value=1, max_value=50), label="prec")
    ctx = Context(prec=prec, rounding=ROUND_HALF_EVEN)

    try:
        result = value.quantize(exp_template, context=ctx)
    except InvalidOperation:
        # Legitimate per docs: coefficient too long, or exponent out of range.
        return

    # Property 1: resulting exponent equals the second operand's exponent.
    _, result_digits, result_exp = result.as_tuple()
    _, _, template_exp = exp_template.as_tuple()
    assert result_exp == template_exp, (
        f"Result exponent {result_exp} != template exponent {template_exp}"
    )

    # Property 2: coefficient length must not exceed context precision on success.
    assert len(result_digits) <= ctx.prec, (
        f"Coefficient length {len(result_digits)} exceeds precision {ctx.prec}"
    )

    # Property 3: result is within one ULP of the original value.
    # One ULP at the target exponent is Decimal(1).scaleb(template_exp).
    with localcontext() as c:
        c.prec = max(prec, 60)
        ulp = Decimal(1).scaleb(template_exp, context=c)
        diff = abs(result - value)
        # Rounding can move the value by at most one ULP.
        assert diff <= ulp, (
            f"|result - value| = {diff} exceeds one ULP {ulp} "
            f"(value={value}, result={result})"
        )
# End program