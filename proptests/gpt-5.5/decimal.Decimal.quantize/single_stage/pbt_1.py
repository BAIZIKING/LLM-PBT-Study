from decimal import (
    Context,
    Decimal,
    InvalidOperation,
    Underflow,
    ROUND_05UP,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
)
from hypothesis import given, strategies as st

# Summary: Generate finite Decimal operands from signed integer coefficients and varied exponents, biasing the quantizer exponent around Etiny(), Emin, 0, Emax, and just-outside bounds. Generate small Contexts with varied precision/Emin/Emax and every rounding mode, sometimes passing an explicit rounding and sometimes relying on the context. Check against a high-precision reference: successful results must equal the reference-rounded value, have the quantizer's exponent, and fit the context precision; documented error cases must signal InvalidOperation; Underflow must never be signaled.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    roundings = [
        ROUND_CEILING,
        ROUND_DOWN,
        ROUND_FLOOR,
        ROUND_HALF_DOWN,
        ROUND_HALF_EVEN,
        ROUND_HALF_UP,
        ROUND_UP,
        ROUND_05UP,
    ]

    def finite_decimal(sign, coefficient, exponent):
        digits = tuple(map(int, str(abs(coefficient)))) if coefficient else (0,)
        return Decimal((sign, digits, exponent))

    prec = data.draw(st.integers(min_value=1, max_value=12))
    emin = data.draw(st.integers(min_value=-12, max_value=0))
    emax = data.draw(st.integers(min_value=0, max_value=12))
    context_rounding = data.draw(st.sampled_from(roundings))

    ctx = Context(prec=prec, Emin=emin, Emax=emax, rounding=context_rounding)
    for signal in ctx.traps:
        ctx.traps[signal] = False

    etiny = ctx.Etiny()

    quantizer_exponent = data.draw(
        st.one_of(
            st.integers(min_value=etiny - 3, max_value=emax + 3),
            st.sampled_from([etiny - 1, etiny, emin, -1, 0, 1, emax, emax + 1]),
        )
    )
    quantizer = Decimal((0, (1,), quantizer_exponent))

    coefficient = data.draw(
        st.one_of(
            st.just(0),
            st.sampled_from([1, 5, 9, 10, 11, 99, 100, 101, 999, 1000, 9999]),
            st.integers(min_value=1, max_value=10**15),
        )
    )
    sign = data.draw(st.integers(min_value=0, max_value=1))
    operand_exponent = data.draw(
        st.one_of(
            st.integers(min_value=-25, max_value=25),
            st.integers(min_value=quantizer_exponent - 8, max_value=quantizer_exponent + 8),
            st.sampled_from([quantizer_exponent - 1, quantizer_exponent, quantizer_exponent + 1]),
        )
    )
    operand = finite_decimal(sign, coefficient, operand_exponent)

    rounding_arg = data.draw(st.one_of(st.none(), st.sampled_from(roundings)))
    effective_rounding = context_rounding if rounding_arg is None else rounding_arg

    ref_ctx = Context(prec=200, Emin=-999999, Emax=999999, rounding=effective_rounding)
    for signal in ref_ctx.traps:
        ref_ctx.traps[signal] = False

    expected = operand.quantize(quantizer, rounding=effective_rounding, context=ref_ctx)
    assert expected.is_finite()

    ctx.clear_flags()
    result = operand.quantize(quantizer, rounding=rounding_arg, context=ctx)

    expected_invalid_operation = (
        quantizer_exponent > ctx.Emax
        or quantizer_exponent < ctx.Etiny()
        or len(expected.as_tuple().digits) > ctx.prec
        or expected.adjusted() > ctx.Emax
    )

    assert not ctx.flags[Underflow]

    if expected_invalid_operation:
        assert result.is_nan()
        assert ctx.flags[InvalidOperation]
    else:
        assert result == expected
        assert result.as_tuple().exponent == quantizer_exponent
        assert len(result.as_tuple().digits) <= ctx.prec
        assert ctx.Etiny() <= result.as_tuple().exponent <= ctx.Emax
        assert not ctx.flags[InvalidOperation]
# End program