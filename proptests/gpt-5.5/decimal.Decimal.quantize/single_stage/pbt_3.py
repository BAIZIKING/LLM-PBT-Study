from hypothesis import given, strategies as st

from decimal import (
    Decimal,
    Context,
    DecimalException,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    ROUND_05UP,
    Clamped,
    DivisionByZero,
    FloatOperation,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
    localcontext,
)

ROUNDINGS = [
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    ROUND_05UP,
]

SIGNALS = [
    Clamped,
    DivisionByZero,
    FloatOperation,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
]


def make_context(prec, emin, emax, rounding, trap_values):
    ctx = Context(prec=prec, Emin=emin, Emax=emax, rounding=rounding)
    for signal, trapped in zip(SIGNALS, trap_values):
        ctx.traps[signal] = trapped
    return ctx


context_strategy = st.builds(
    make_context,
    prec=st.integers(min_value=1, max_value=30),
    emin=st.integers(min_value=-30, max_value=0),
    emax=st.integers(min_value=0, max_value=30),
    rounding=st.sampled_from(ROUNDINGS),
    trap_values=st.lists(st.booleans(), min_size=len(SIGNALS), max_size=len(SIGNALS)),
)


def decimal_strategy_for(ctx):
    interesting_exponents = [
        ctx.Etiny() - 1,
        ctx.Etiny(),
        ctx.Etiny() + 1,
        ctx.Emin - 1,
        ctx.Emin,
        ctx.Emin + 1,
        -1,
        0,
        1,
        ctx.Emax - 1,
        ctx.Emax,
        ctx.Emax + 1,
    ]
    exponent_strategy = st.one_of(
        st.sampled_from(interesting_exponents),
        st.integers(
            min_value=min(ctx.Etiny() - 5, -50),
            max_value=max(ctx.Emax + 5, 50),
        ),
    )

    finite_decimals = st.builds(
        lambda sign, digits, exponent: Decimal((sign, tuple(digits), exponent)),
        sign=st.integers(min_value=0, max_value=1),
        digits=st.lists(
            st.integers(min_value=0, max_value=9),
            min_size=1,
            max_size=ctx.prec + 8,
        ),
        exponent=exponent_strategy,
    )

    special_decimals = st.sampled_from(
        [
            Decimal("NaN"),
            Decimal("-NaN"),
            Decimal("sNaN"),
            Decimal("-sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ]
    )

    return st.one_of(finite_decimals, special_decimals)


# Summary: Generate Decimal operands with varied signs, zeros, coefficient lengths, exponents near Etiny/Emin/Emax, NaNs, sNaNs, and infinities; generate optional rounding modes and optional Context objects with varied precision, exponent bounds, rounding, and traps. Check that quantize never signals Underflow, that successful finite results have the exponent of exp and a coefficient no longer than context precision, and that finite quantizations whose target exponent is outside [Etiny(), Emax] signal InvalidOperation.
@given(st.data())
def test_decimal_Decimal_quantize(data):
    ctx = data.draw(context_strategy)
    x = data.draw(decimal_strategy_for(ctx))
    exp = data.draw(decimal_strategy_for(ctx))
    rounding = data.draw(st.one_of(st.none(), st.sampled_from(ROUNDINGS)))
    pass_context_argument = data.draw(st.booleans())

    current_ctx_template = ctx.copy()
    explicit_ctx = ctx.copy()
    current_ctx_template.clear_flags()
    explicit_ctx.clear_flags()

    with localcontext(current_ctx_template) as current_ctx:
        current_ctx.clear_flags()

        kwargs = {}
        if rounding is not None:
            kwargs["rounding"] = rounding

        if pass_context_argument:
            kwargs["context"] = explicit_ctx
            active_ctx = explicit_ctx
        else:
            active_ctx = current_ctx

        finite_operands = x.is_finite() and exp.is_finite()
        exp_exponent = exp.as_tuple().exponent if finite_operands else None
        target_exponent_out_of_range = (
            finite_operands
            and (exp_exponent > active_ctx.Emax or exp_exponent < active_ctx.Etiny())
        )

        try:
            result = x.quantize(exp, **kwargs)
        except DecimalException as exc:
            assert not isinstance(exc, Underflow)
            assert active_ctx.flags[Underflow] is False

            if target_exponent_out_of_range:
                assert isinstance(exc, InvalidOperation)
            return

        assert active_ctx.flags[Underflow] is False

        if target_exponent_out_of_range:
            assert active_ctx.flags[InvalidOperation] is True
            assert result.is_nan()
            return

        if finite_operands and result.is_finite():
            assert result.as_tuple().exponent == exp_exponent
            assert len(result.as_tuple().digits) <= active_ctx.prec
# End program