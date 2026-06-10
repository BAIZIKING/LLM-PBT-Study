from hypothesis import given, strategies as st
from decimal import (
    Decimal, Context, localcontext, InvalidOperation,
    ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_HALF_DOWN,
    ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR, ROUND_05UP,
)

# Summary: Generate a first Decimal operand (finite/special, varied precision &
# magnitude), an exp Decimal whose exponent spans small-to-large values, an
# optional rounding mode, and a context with varied precision to exercise
# rounding, InvalidOperation (coefficient too long / exp out of range), and
# special-value handling. Assert that either a decimal error is raised or the
# result's exponent equals exp's exponent (and value-preservation when no change).
@given(st.data())
def test_decimal_Decimal_quantize():
    data = st.data().example if False else None  # placeholder, unused

    raise_strategy = None  # not used; we use the bound `data` below


@given(st.data())
def test_decimal_Decimal_quantize(data):
    # First operand: finite values, specials, varied precision/magnitude.
    value = data.draw(
        st.decimals(
            allow_nan=True,
            allow_infinity=True,
            min_value=None,
            max_value=None,
            places=None,
        )
    )

    # exp: a Decimal whose exponent is what we quantize to.
    exp_exponent = data.draw(st.integers(min_value=-20, max_value=20))
    coeff_for_exp = data.draw(st.sampled_from(["1", "10", "100", "0", "5"]))
    # Build exp with the desired exponent: e.g. exponent -3 -> Decimal('1E-3')
    exp = Decimal(coeff_for_exp).scaleb(exp_exponent)
    # Ensure exp has a clean single exponent for the comparison.
    exp = exp.normalize() if exp.is_finite() and exp != 0 else exp
    # Re-derive a controlled exp directly from exponent for reliability:
    exp = Decimal((0, (1,), exp_exponent))  # value 1Eexp_exponent

    # Rounding mode (or None).
    rounding = data.draw(
        st.sampled_from([
            None, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_HALF_DOWN,
            ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR, ROUND_05UP,
        ])
    )

    # Context with varied precision.
    prec = data.draw(st.integers(min_value=1, max_value=50))
    use_context = data.draw(st.booleans())
    ctx = Context(prec=prec) if use_context else None

    target_exponent = exp.as_tuple()[2]  # the exponent we expect on success

    try:
        result = value.quantize(exp, rounding=rounding, context=ctx)
    except (InvalidOperation, ValueError) as e:
        # Allowed: coefficient too long for precision, exp out of [Etiny, Emax],
        # or quantizing infinity / signaling NaN, etc.
        return
    except Exception as e:
        # No other exception type should escape from a well-formed quantize call.
        raise AssertionError(f"Unexpected exception type: {type(e).__name__}: {e}")

    # Property 5: Special-value propagation.
    if result.is_nan():
        # Result NaN is only valid if an operand was NaN.
        assert value.is_nan() or exp.is_nan(), (
            "quantize produced NaN without a NaN operand"
        )
        return

    if result.is_infinite():
        # Infinite result only valid if value was infinite and exp infinite too.
        assert value.is_infinite() and exp.is_infinite(), (
            "quantize produced infinity unexpectedly"
        )
        return

    # Property 1: On finite success, exponent must equal exp's exponent.
    assert result.as_tuple()[2] == target_exponent, (
        f"Result exponent {result.as_tuple()[2]} != exp exponent {target_exponent}; "
        f"value={value!r}, exp={exp!r}, result={result!r}"
    )

    # Property 3 (value preservation): the result should be numerically close to
    # the original value, differing by at most one ULP of the target exponent
    # (i.e. the magnitude of the rounding step).
    if value.is_finite():
        ulp = Decimal((0, (1,), target_exponent))
        diff = abs(value - result)
        assert diff <= ulp, (
            f"quantize changed value by more than one ULP: "
            f"value={value!r}, result={result!r}, diff={diff}, ulp={ulp}"
        )
# End program