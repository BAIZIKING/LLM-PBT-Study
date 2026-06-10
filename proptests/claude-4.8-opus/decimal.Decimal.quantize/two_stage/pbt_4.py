from hypothesis import given, strategies as st, assume, settings
import decimal
from decimal import Decimal, InvalidOperation, Overflow, Clamped


# Strategy for generating finite Decimal values with controlled magnitude
def finite_decimals():
    return st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e20"),
        max_value=Decimal("1e20"),
        places=None,
    )


# Strategy for generating "exp" Decimals (the target exponent operand).
# We keep their exponent in a modest range to avoid trivial overflows.
def exp_decimals():
    return st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e10"),
        max_value=Decimal("1e10"),
        places=None,
    ).filter(lambda d: d.is_finite())


def rounding_modes():
    return st.sampled_from([
        None,
        decimal.ROUND_CEILING,
        decimal.ROUND_DOWN,
        decimal.ROUND_FLOOR,
        decimal.ROUND_HALF_DOWN,
        decimal.ROUND_HALF_EVEN,
        decimal.ROUND_HALF_UP,
        decimal.ROUND_UP,
        decimal.ROUND_05UP,
    ])


@given(st.data())
@settings(max_examples=500)
def test_decimal_Decimal_quantize_property(data):
    # ---- Property 1 ----
    # The exponent of the result is always equal to the exponent of the
    # second operand (`exp`), unless an error/exception is raised.
    first = data.draw(finite_decimals(), label="first")
    exp = data.draw(exp_decimals(), label="exp")
    rounding = data.draw(rounding_modes(), label="rounding")
    ctx = decimal.Context(prec=28)
    try:
        result = first.quantize(exp, rounding=rounding, context=ctx)
    except (InvalidOperation, Overflow):
        pass
    else:
        assert result.as_tuple().exponent == exp.as_tuple().exponent

    # ---- Property 2 ----
    # The result is numerically equal to the first operand when no rounding
    # is required, and otherwise differs by less than one ulp of target exp.
    first2 = data.draw(finite_decimals(), label="first2")
    exp2 = data.draw(exp_decimals(), label="exp2")
    rounding2 = data.draw(rounding_modes(), label="rounding2")
    ctx2 = decimal.Context(prec=28)
    try:
        result2 = first2.quantize(exp2, rounding=rounding2, context=ctx2)
    except (InvalidOperation, Overflow):
        pass
    else:
        target_exp = exp2.as_tuple().exponent
        ulp = Decimal(1).scaleb(target_exp)
        # Difference between original and quantized must be strictly < 1 ulp.
        diff = abs(first2 - result2)
        assert diff < ulp or diff == 0

    # ---- Property 3 ----
    # The number of significant digits in the result never exceeds context
    # precision; if it would, InvalidOperation is signaled.
    first3 = data.draw(finite_decimals(), label="first3")
    exp3 = data.draw(exp_decimals(), label="exp3")
    rounding3 = data.draw(rounding_modes(), label="rounding3")
    prec = data.draw(st.integers(min_value=1, max_value=40), label="prec")
    ctx3 = decimal.Context(prec=prec)
    try:
        result3 = first3.quantize(exp3, rounding=rounding3, context=ctx3)
    except (InvalidOperation, Overflow):
        pass
    else:
        digits = result3.as_tuple().digits
        # Number of significant digits in the coefficient.
        assert len(digits) <= prec

    # ---- Property 4 ----
    # When rounding is required, the result respects the rounding mode.
    # Verify ROUND_FLOOR <= ROUND_HALF_EVEN <= ROUND_CEILING etc. ordering.
    first4 = data.draw(finite_decimals(), label="first4")
    exp4 = data.draw(exp_decimals(), label="exp4")
    ctx4 = decimal.Context(prec=28)
    try:
        r_floor = first4.quantize(exp4, rounding=decimal.ROUND_FLOOR, context=ctx4)
        r_ceil = first4.quantize(exp4, rounding=decimal.ROUND_CEILING, context=ctx4)
        r_down = first4.quantize(exp4, rounding=decimal.ROUND_DOWN, context=ctx4)
        r_up = first4.quantize(exp4, rounding=decimal.ROUND_UP, context=ctx4)
    except (InvalidOperation, Overflow):
        pass
    else:
        # Floor never exceeds ceiling.
        assert r_floor <= r_ceil
        # Down (toward zero) magnitude never exceeds up (away from zero).
        assert abs(r_down) <= abs(r_up)

    # ---- Property 5 ----
    # Underflow is never signaled; subnormal/inexact small results do not
    # raise Underflow. Quantizing to a representable exponent within Etiny
    # bounds should not raise Underflow.
    first5 = data.draw(finite_decimals(), label="first5")
    exp5 = data.draw(exp_decimals(), label="exp5")
    rounding5 = data.draw(rounding_modes(), label="rounding5")
    ctx5 = decimal.Context(prec=28)
    ctx5.traps[decimal.Underflow] = True  # If Underflow were signaled, raise.
    try:
        result5 = first5.quantize(exp5, rounding=rounding5, context=ctx5)
    except decimal.Underflow:
        # This must never happen per the documentation.
        assert False, "quantize must never signal Underflow"
    except (InvalidOperation, Overflow):
        pass
    else:
        # A successful result is fine; no Underflow trap fired.
        assert result5.is_finite()
# End program