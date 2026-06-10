from hypothesis import given, strategies as st, assume
import decimal
from decimal import Decimal, Context, localcontext

# Strategy for generating reasonable Decimal values to avoid overflow / invalid ops
def decimal_strategy():
    return st.one_of(
        st.integers(min_value=-10**6, max_value=10**6).map(Decimal),
        st.floats(
            allow_nan=False, allow_infinity=False,
            min_value=-1e6, max_value=1e6
        ).map(lambda f: Decimal(repr(f))),
        st.decimals(
            min_value=Decimal(-10**6), max_value=Decimal(10**6),
            allow_nan=False, allow_infinity=False
        ),
    )


@given(st.data())
def test_decimal_Decimal_fma_property(data):
    a = data.draw(decimal_strategy(), label="a")
    b = data.draw(decimal_strategy(), label="b")
    c = data.draw(decimal_strategy(), label="c")

    # Use a high-precision context for comparisons against the exact value
    ctx = Context(prec=50)

    # Property 1: result equals self*other+third with no rounding of the
    # intermediate product, i.e. matches exact value rounded once.
    with localcontext(Context(prec=200)):
        exact = a * b + c  # high enough precision to be effectively exact
    fma_result = a.fma(b, c, ctx)
    with localcontext(Context(prec=200)):
        expected_rounded = +Decimal(exact) if False else exact
    # Compare fma result against exact value rounded to ctx precision
    rounded_exact = ctx.create_decimal(exact)
    assert fma_result == rounded_exact, (
        f"fma({a},{b},{c}) = {fma_result}, expected {rounded_exact}"
    )

    # Property 2: when third is zero, result equals self*other (rounded)
    zero = Decimal(0)
    fma_zero_third = a.fma(b, zero, ctx)
    mult_result = ctx.multiply(a, b)
    assert fma_zero_third == mult_result, (
        f"fma({a},{b},0) = {fma_zero_third}, expected {mult_result}"
    )

    # Property 3: when self or other is zero, result equals third
    fma_zero_self = zero.fma(b, c, ctx)
    expected_c = ctx.create_decimal(c)
    assert fma_zero_self == expected_c, (
        f"fma(0,{b},{c}) = {fma_zero_self}, expected {expected_c}"
    )
    fma_zero_other = a.fma(zero, c, ctx)
    assert fma_zero_other == expected_c, (
        f"fma({a},0,{c}) = {fma_zero_other}, expected {expected_c}"
    )

    # Property 4: commutativity of multiplication arguments
    fma_ab = a.fma(b, c, ctx)
    fma_ba = b.fma(a, c, ctx)
    assert fma_ab == fma_ba, (
        f"fma({a},{b},{c})={fma_ab} != fma({b},{a},{c})={fma_ba}"
    )

    # Property 5: fma result never has larger rounding error than two-step
    two_step = ctx.add(ctx.multiply(a, b), c)
    with localcontext(Context(prec=200)):
        err_fma = abs(Decimal(fma_result) - Decimal(exact))
        err_two_step = abs(Decimal(two_step) - Decimal(exact))
    assert err_fma <= err_two_step, (
        f"fma error {err_fma} exceeds two-step error {err_two_step} "
        f"for fma({a},{b},{c})"
    )
# End program