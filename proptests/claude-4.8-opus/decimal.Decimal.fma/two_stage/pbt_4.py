from hypothesis import given, strategies as st, assume, settings
import decimal
from decimal import Decimal, Context, InvalidOperation, getcontext


# Strategy for generating "reasonable" Decimal values to avoid extreme overflow.
# We bound the exponents and the number of digits to keep intermediate products manageable.
def finite_decimals(min_value=-1e15, max_value=1e15):
    return st.one_of(
        st.integers(min_value=-10**12, max_value=10**12).map(Decimal),
        st.floats(
            min_value=min_value,
            max_value=max_value,
            allow_nan=False,
            allow_infinity=False,
        ).map(lambda f: Decimal(repr(f))),
    )


# A wide context to allow exact computations with enough precision.
WIDE = Context(prec=200, Emax=999999, Emin=-999999)


@given(st.data())
@settings(max_examples=500)
def test_decimal_Decimal_fma_property(data):
    # Draw three finite decimal operands.
    a = data.draw(finite_decimals(), label="a")
    b = data.draw(finite_decimals(), label="b")
    c = data.draw(finite_decimals(), label="c")

    ctx = WIDE

    # ------------------------------------------------------------------
    # Property 1: fma equals self*other + third with exact intermediate
    # product, then rounded under the context.
    # ------------------------------------------------------------------
    fma_result = a.fma(b, c, context=ctx)
    # Compute exact intermediate product, then add third under ctx.
    exact_product = a * b  # exact for Decimal multiplication (no rounding needed for these sizes)
    expected = ctx.add(exact_product, c)
    assert fma_result == expected, (
        f"Property1 failed: {a}.fma({b}, {c}) = {fma_result}, expected {expected}"
    )

    # ------------------------------------------------------------------
    # Property 2: third == 0 -> result equals product rounded under ctx.
    # ------------------------------------------------------------------
    zero = Decimal(0)
    fma_zero = a.fma(b, zero, context=ctx)
    expected_product = ctx.multiply(a, b)
    assert fma_zero == expected_product, (
        f"Property2 failed: {a}.fma({b}, 0) = {fma_zero}, expected {expected_product}"
    )

    # ------------------------------------------------------------------
    # Property 3: other == 1 -> result equals self + third under ctx.
    # ------------------------------------------------------------------
    one = Decimal(1)
    fma_one = a.fma(one, c, context=ctx)
    expected_sum = ctx.add(a, c)
    assert fma_one == expected_sum, (
        f"Property3 failed: {a}.fma(1, {c}) = {fma_one}, expected {expected_sum}"
    )

    # ------------------------------------------------------------------
    # Property 4: self == 0 (and other finite) -> result equals third.
    # ------------------------------------------------------------------
    fma_self_zero = zero.fma(b, c, context=ctx)
    expected_third = ctx.add(Decimal(0), c)  # 0*b + c, normalized through context add
    assert fma_self_zero == expected_third, (
        f"Property4 failed: 0.fma({b}, {c}) = {fma_self_zero}, expected {expected_third}"
    )

    # ------------------------------------------------------------------
    # Property 5: NaN / signaling NaN / invalid product behavior.
    # ------------------------------------------------------------------
    # Quiet NaN operand with valid product -> NaN result.
    qnan = Decimal("NaN")
    trap_ctx = Context(prec=200, Emax=999999, Emin=-999999, traps=[InvalidOperation])

    # quiet NaN should produce NaN (no trap raised for quiet NaN in these positions).
    res_qnan = a.fma(b, qnan)  # uses default behavior; quiet NaN propagates
    assert res_qnan.is_nan(), (
        f"Property5 failed: quiet NaN third did not propagate to NaN, got {res_qnan}"
    )

    # 0 * infinity is an invalid operation -> should raise InvalidOperation under trapping ctx.
    inf = Decimal("Infinity")
    try:
        zero.fma(inf, c, context=trap_ctx)
        raised = False
    except InvalidOperation:
        raised = True
    assert raised, (
        "Property5 failed: 0 * Infinity in fma did not raise InvalidOperation under trapping context"
    )

    # Signaling NaN should raise InvalidOperation under trapping context.
    snan = Decimal("sNaN")
    try:
        a.fma(b, snan, context=trap_ctx)
        raised_snan = False
    except InvalidOperation:
        raised_snan = True
    assert raised_snan, (
        "Property5 failed: signaling NaN in fma did not raise InvalidOperation"
    )
# End program