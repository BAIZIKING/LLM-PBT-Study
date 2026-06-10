from hypothesis import given, strategies as st
from decimal import (
    Decimal,
    Context,
    InvalidOperation,
    Underflow,
    localcontext,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_UP,
    ROUND_DOWN,
    ROUND_HALF_UP,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_05UP,
)

ROUNDING_MODES = (
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_UP,
    ROUND_DOWN,
    ROUND_HALF_UP,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_05UP,
)

# Summary: Generate finite Decimals from explicit signs, coefficient digit tuples, and exponents.
# The context precision/Emin/Emax are randomized, and target exponents are biased around
# Etiny(), Emin, 0, Emax, and just outside the valid exponent range. Coefficient lengths are
# biased around the context precision to trigger both successful quantization and
# InvalidOperation. The test also varies explicit rounding modes and omitted/passed contexts.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    prec = data.draw(st.integers(min_value=1, max_value=12))
    emin = data.draw(st.integers(min_value=-12, max_value=0))
    emax = data.draw(st.integers(min_value=0, max_value=12))
    ctx_rounding = data.draw(st.sampled_from(ROUNDING_MODES))

    base_ctx = Context(prec=prec, Emin=emin, Emax=emax, rounding=ctx_rounding)
    for signal in list(base_ctx.traps):
        base_ctx.traps[signal] = False
    base_ctx.traps[Underflow] = True
    base_ctx.clear_flags()

    etiny = base_ctx.Etiny()

    def draw_digits(max_len):
        kind = data.draw(
            st.sampled_from(
                ["zero", "one", "nines", "power_of_ten", "trailing_zeros", "random"]
            )
        )
        if kind == "zero":
            return (0,)

        length = data.draw(st.integers(min_value=1, max_value=max_len))

        if kind == "one":
            return (1,)
        if kind == "nines":
            return tuple([9] * length)
        if kind == "power_of_ten":
            return (1,) + tuple([0] * (length - 1))
        if kind == "trailing_zeros":
            first = data.draw(st.integers(min_value=1, max_value=9))
            return (first,) + tuple([0] * (length - 1))

        first = data.draw(st.integers(min_value=1, max_value=9))
        rest = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=9),
                min_size=length - 1,
                max_size=length - 1,
            )
        )
        return (first, *rest)

    interesting_target_exponents = [
        etiny - 2,
        etiny - 1,
        etiny,
        etiny + 1,
        emin,
        -prec,
        -1,
        0,
        1,
        emax,
        emax + 1,
        emax + 2,
    ]
    target_exp = data.draw(
        st.one_of(
            st.sampled_from(interesting_target_exponents),
            st.integers(min_value=etiny - 5, max_value=emax + 5),
        )
    )

    max_coeff_len = prec + 8

    x_exp = data.draw(
        st.one_of(
            st.sampled_from(
                [
                    target_exp - 3,
                    target_exp - 1,
                    target_exp,
                    target_exp + 1,
                    target_exp + 3,
                    etiny - 2,
                    etiny,
                    emin,
                    0,
                    emax,
                    emax + 1,
                ]
            ),
            st.integers(min_value=etiny - 5, max_value=emax + 5),
        )
    )

    x = Decimal(
        (
            data.draw(st.integers(min_value=0, max_value=1)),
            draw_digits(max_coeff_len),
            x_exp,
        )
    )
    exp = Decimal(
        (
            data.draw(st.integers(min_value=0, max_value=1)),
            draw_digits(max_coeff_len),
            target_exp,
        )
    )

    rounding_arg = data.draw(st.one_of(st.none(), st.sampled_from(ROUNDING_MODES)))
    omit_context = data.draw(st.booleans())

    def same_decimal(a, b):
        return a.compare_total(b) == Decimal(0)

    def snapshot_flags(ctx):
        return {signal: bool(ctx.flags[signal]) for signal in ctx.flags}

    def run_quantize(ctx, explicit_rounding, use_current_context):
        ctx = ctx.copy()
        ctx.clear_flags()

        try:
            if use_current_context:
                with localcontext(ctx) as current:
                    current.clear_flags()
                    if explicit_rounding is None:
                        result = x.quantize(exp)
                    else:
                        result = x.quantize(exp, rounding=explicit_rounding)
                    return result, snapshot_flags(current), current.prec, current.Emax, current.Etiny()
            else:
                result = x.quantize(exp, rounding=explicit_rounding, context=ctx)
                return result, snapshot_flags(ctx), ctx.prec, ctx.Emax, ctx.Etiny()
        except Underflow:
            assert False, "quantize() must never signal Underflow"

    result, flags, effective_prec, effective_emax, effective_etiny = run_quantize(
        base_ctx, rounding_arg, omit_context
    )

    assert flags[Underflow] is False

    invalid = flags[InvalidOperation]
    resulting_exponent_would_be = exp.as_tuple().exponent

    if (
        resulting_exponent_would_be > effective_emax
        or resulting_exponent_would_be < effective_etiny
    ):
        assert invalid, "out-of-range quantized exponent must signal InvalidOperation"

    if invalid:
        assert result.is_qnan()
    else:
        assert result.is_finite()
        assert result.as_tuple().exponent == exp.as_tuple().exponent
        assert len(result.as_tuple().digits) <= effective_prec
        assert effective_etiny <= result.as_tuple().exponent <= effective_emax

        if x.as_tuple().exponent == exp.as_tuple().exponent:
            assert same_decimal(result, x)

    explicit_ctx_result, explicit_ctx_flags, _, _, _ = run_quantize(
        base_ctx, rounding_arg, use_current_context=False
    )
    current_ctx_result, current_ctx_flags, _, _, _ = run_quantize(
        base_ctx, rounding_arg, use_current_context=True
    )

    assert same_decimal(explicit_ctx_result, current_ctx_result)
    assert explicit_ctx_flags == current_ctx_flags

    if rounding_arg is not None:
        different_context_rounding = next(
            mode for mode in ROUNDING_MODES if mode != rounding_arg
        )

        ctx_with_different_rounding = base_ctx.copy()
        ctx_with_different_rounding.rounding = different_context_rounding

        ctx_with_requested_rounding = base_ctx.copy()
        ctx_with_requested_rounding.rounding = rounding_arg

        explicit_rounding_result, explicit_rounding_flags, _, _, _ = run_quantize(
            ctx_with_different_rounding,
            rounding_arg,
            use_current_context=False,
        )
        context_rounding_result, context_rounding_flags, _, _, _ = run_quantize(
            ctx_with_requested_rounding,
            None,
            use_current_context=False,
        )

        assert same_decimal(explicit_rounding_result, context_rounding_result)
        assert explicit_rounding_flags == context_rounding_flags

# End program