from hypothesis import given, strategies as st
from decimal import (
    Decimal,
    Context,
    InvalidOperation,
    Underflow,
    localcontext,
    ROUND_05UP,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
)

# Summary: Generate finite Decimals with varied signs, zeros, coefficient lengths, and exponents around
# the active Context's Emin/Emax/Etiny boundaries. Generate quantizer Decimals whose exponent is often
# exactly at, just inside, or just outside the valid exponent range. Randomize precision, rounding mode,
# whether an explicit rounding argument is passed, and whether an explicit context argument is passed.
# Check that successful quantize calls have the quantizer's exponent, do not exceed context precision,
# preserve numeric value when no rounding is needed, respect the documented rounding-argument precedence,
# signal InvalidOperation for out-of-range result exponents, and never signal Underflow.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    roundings = [
        ROUND_CEILING,
        ROUND_FLOOR,
        ROUND_UP,
        ROUND_DOWN,
        ROUND_HALF_UP,
        ROUND_HALF_DOWN,
        ROUND_HALF_EVEN,
        ROUND_05UP,
    ]

    prec = data.draw(st.integers(min_value=1, max_value=30))
    emin = data.draw(st.integers(min_value=-30, max_value=0))
    emax = data.draw(st.integers(min_value=0, max_value=30))
    context_rounding = data.draw(st.sampled_from(roundings))

    ctx = Context(prec=prec, Emin=emin, Emax=emax, rounding=context_rounding)
    for signal in ctx.traps:
        ctx.traps[signal] = False
    ctx.traps[InvalidOperation] = True
    ctx.traps[Underflow] = True

    etiny = ctx.Etiny()

    target_exp = data.draw(
        st.one_of(
            st.sampled_from(
                [
                    etiny - 1,
                    etiny,
                    etiny + 1,
                    emin - 1,
                    emin,
                    emin + 1,
                    -1,
                    0,
                    1,
                    emax - 1,
                    emax,
                    emax + 1,
                ]
            ),
            st.integers(min_value=etiny - 5, max_value=emax + 5),
        )
    )

    x_exp = data.draw(
        st.one_of(
            st.sampled_from(
                [
                    target_exp - 2,
                    target_exp - 1,
                    target_exp,
                    target_exp + 1,
                    target_exp + 2,
                    etiny,
                    emin,
                    0,
                    emax,
                ]
            ),
            st.integers(min_value=etiny - 5, max_value=emax + 5),
        )
    )

    def draw_finite_decimal(exponent, max_digits):
        sign = int(data.draw(st.booleans()))
        interesting_lengths = sorted(
            {
                n
                for n in [
                    1,
                    2,
                    max(1, prec - 1),
                    prec,
                    prec + 1,
                    prec + 10,
                    max_digits,
                ]
                if 1 <= n <= max_digits
            }
        )
        n_digits = data.draw(
            st.one_of(
                st.sampled_from(interesting_lengths),
                st.integers(min_value=1, max_value=max_digits),
            )
        )

        if data.draw(st.booleans()):
            digits = (0,) * n_digits
        else:
            first = data.draw(st.integers(min_value=1, max_value=9))
            rest = data.draw(
                st.lists(
                    st.integers(min_value=0, max_value=9),
                    min_size=n_digits - 1,
                    max_size=n_digits - 1,
                )
            )
            digits = (first, *rest)

        return Decimal((sign, digits, exponent))

    x = draw_finite_decimal(x_exp, max_digits=40)
    quantizer = draw_finite_decimal(target_exp, max_digits=5)

    rounding_arg = data.draw(st.one_of(st.none(), st.sampled_from(roundings)))
    pass_context_argument = data.draw(st.booleans())

    with localcontext(ctx) as active:
        active.clear_flags()
        out_of_range_exponent = target_exp > active.Emax or target_exp < active.Etiny()

        try:
            if pass_context_argument:
                result = x.quantize(
                    quantizer,
                    rounding=rounding_arg,
                    context=active,
                )
            else:
                result = x.quantize(
                    quantizer,
                    rounding=rounding_arg,
                )
        except Underflow as exc:
            raise AssertionError("quantize must never signal Underflow") from exc
        except InvalidOperation:
            assert active.flags[InvalidOperation]
            assert not active.flags[Underflow]
            return

        assert not active.flags[Underflow]
        assert not out_of_range_exponent
        assert result.as_tuple().exponent == quantizer.as_tuple().exponent
        assert len(result.as_tuple().digits) <= active.prec

        if target_exp <= x_exp:
            assert result == x

        reference_context = active.copy()
        reference_context.clear_flags()
        if rounding_arg is not None:
            reference_context.rounding = rounding_arg

        expected = x.quantize(quantizer, context=reference_context)
        assert not reference_context.flags[Underflow]
        assert result == expected
        assert result.as_tuple().exponent == expected.as_tuple().exponent
# End program