from hypothesis import given, strategies as st, assume
from decimal import (Decimal, localcontext, InvalidOperation, Overflow,
                     ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP, ROUND_CEILING,
                     ROUND_FLOOR, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_05UP,
                     Inexact, Rounded)

# Summary: Generate the value-operand from floats/ints/decimal-strings with varied
# magnitudes & significant digits; generate the exp-operand as Decimals with a
# controlled exponent range; pick rounding from None or all valid modes. On a
# successful quantize, assert exponent equality, coefficient-length <= precision,
# no Underflow signaled, and idempotence/closeness to the original value.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    rounding_modes = [None, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP,
                      ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP,
                      ROUND_HALF_DOWN, ROUND_05UP]

    # Strategy for the first operand (the value to quantize) - finite decimals.
    value_strategy = st.one_of(
        st.integers(min_value=-10**12, max_value=10**12).map(Decimal),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e15, max_value=1e15).map(lambda f: Decimal(repr(f))),
        st.tuples(
            st.integers(min_value=-10**18, max_value=10**18),
            st.integers(min_value=-15, max_value=10),
        ).map(lambda t: Decimal(t[0]).scaleb(t[1])),
    )
    value = data.draw(value_strategy)

    # Strategy for the second operand: only its exponent matters.
    exp_value = data.draw(st.integers(min_value=-15, max_value=10))
    exp = Decimal(1).scaleb(exp_value)

    rounding = data.draw(st.sampled_from(rounding_modes))
    precision = data.draw(st.integers(min_value=1, max_value=50))

    with localcontext() as ctx:
        ctx.prec = precision
        try:
            result = value.quantize(exp, rounding=rounding)
        except (InvalidOperation, Overflow):
            # Documented error conditions: coefficient too long for precision,
            # or resulting exponent out of [Etiny, Emax]. Accept as valid.
            return

        # Property 2: quantize never signals Underflow.
        # (Underflow flag is keyed under the decimal.Underflow exception class.)
        from decimal import Underflow
        assert ctx.flags[Underflow] == 0

        # Determine the exponent of exp and of the result.
        (_, _, exp_exponent) = exp.as_tuple()
        (sign, digits, res_exponent) = result.as_tuple()

        # Property 1: resulting exponent equals exp's exponent (on success).
        assert res_exponent == exp_exponent, (
            f"exponent {res_exponent} != target {exp_exponent}")

        # Property 3: coefficient length must not exceed precision.
        assert len(digits) <= precision, (
            f"coefficient length {len(digits)} > precision {precision}")

        # Property 4a: idempotence - re-quantizing gives the same result.
        requantized = result.quantize(exp, rounding=rounding)
        assert requantized == result

        # Property 4b: closeness - the result is within one ULP of the target
        # exponent from the original value (rounding error bounded).
        ulp = Decimal(1).scaleb(exp_exponent)
        with localcontext() as ctx2:
            ctx2.prec = 60
            diff = abs(result - value)
        assert diff <= ulp, f"rounding diff {diff} exceeds ulp {ulp}"
# End program