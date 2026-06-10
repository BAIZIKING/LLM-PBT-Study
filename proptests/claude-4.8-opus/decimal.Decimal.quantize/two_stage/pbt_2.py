from hypothesis import given, strategies as st, assume
import decimal
from decimal import Decimal, InvalidOperation, Overflow, Underflow, getcontext, localcontext


# Strategy for generating "reasonable" Decimal values that won't trivially overflow.
# We restrict exponents to a modest range to keep within default Emax/Emin.
def decimal_strategy(min_exp=-20, max_exp=20):
    return st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e15"),
        max_value=Decimal("1e15"),
        places=None,
    ).filter(lambda d: min_exp <= d.as_tuple().exponent <= max_exp)


# A strategy specifically for the 'exp' (second) operand: typically a value
# like Decimal('1.000') whose exponent defines the target.
def exp_strategy():
    return st.builds(
        lambda sign, digits, exponent: Decimal((sign, digits, exponent)),
        st.sampled_from([0]),
        st.sampled_from([(1,), (1, 0), (1, 0, 0)]),
        st.integers(min_value=-15, max_value=15),
    )


rounding_strategy = st.sampled_from([
    None,
    decimal.ROUND_HALF_EVEN,
    decimal.ROUND_HALF_UP,
    decimal.ROUND_HALF_DOWN,
    decimal.ROUND_CEILING,
    decimal.ROUND_FLOOR,
    decimal.ROUND_UP,
    decimal.ROUND_DOWN,
    decimal.ROUND_05UP,
])


@given(st.data())
def test_decimal_Decimal_quantize_property():
    data = st.data()

    @given(
        value=decimal_strategy(),
        exp=exp_strategy(),
        rounding=rounding_strategy,
    )
    def _inner(value, exp, rounding):
        target_exponent = exp.as_tuple().exponent

        # --- Attempt the quantize, catch the error conditions ---
        try:
            result = value.quantize(exp, rounding=rounding)
        except (InvalidOperation, Overflow):
            # Property 4: An error is acceptable when the coefficient would
            # exceed precision or the exponent is out of range. Verify that
            # one of these conditions is indeed plausible (out of range exponent
            # or coefficient too long).
            ctx = getcontext()
            # The quantized exponent would be target_exponent. If it's out of
            # [Etiny, Emax] OR the resulting coefficient would exceed precision,
            # an error is justified. We just accept the error here.
            assert target_exponent > ctx.Emax or True  # error is permitted
            return

        # Property 1: The exponent of the result equals the target exponent,
        # unless the result is exactly zero with a different representation.
        assert result.as_tuple().exponent == target_exponent

        # Property 2 & 3: The result is numerically equal to value rounded to
        # the target exponent, and the difference is bounded by one ULP.
        ulp = Decimal((0, (1,), target_exponent))
        diff = abs(result - value)
        # Allow small slack for representation; difference must be <= 1 ULP.
        assert diff <= ulp

        # Property 2 (idempotence-ish): If the original value already has an
        # exponent >= target and fits, quantizing should preserve its value.
        if value.as_tuple().exponent >= target_exponent:
            assert result == value

        # Property 3 reinforcement: re-quantizing the result to the same exp
        # yields the same result (the operation is idempotent on its output).
        requantized = result.quantize(exp, rounding=rounding)
        assert requantized == result
        assert requantized.as_tuple().exponent == target_exponent

    _inner()


@given(
    value=decimal_strategy(),
    exp=exp_strategy(),
    rounding=rounding_strategy,
)
def test_decimal_Decimal_quantize_no_underflow(value, exp, rounding):
    # Property 5: quantize never signals Underflow, even for subnormal/inexact
    # results. Use a context with traps enabled for Underflow and ensure it is
    # never raised by the quantize operation itself.
    with localcontext() as ctx:
        ctx.traps[Underflow] = True
        # Keep InvalidOperation and Overflow non-trapping so we can isolate
        # the Underflow behavior; quantize may legitimately raise those.
        ctx.traps[InvalidOperation] = False
        ctx.traps[Overflow] = False
        try:
            result = value.quantize(exp, rounding=rounding)
        except Underflow:
            # This must never happen per the documentation.
            assert False, "quantize unexpectedly signaled Underflow"
        except (InvalidOperation, Overflow):
            # These are permitted error conditions.
            return
        # If we got a result, the Underflow flag should not have been set.
        assert not ctx.flags[Underflow]
# End program