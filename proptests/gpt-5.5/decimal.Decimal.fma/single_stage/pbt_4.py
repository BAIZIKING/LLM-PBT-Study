from hypothesis import given, strategies as st
from decimal import (
    Decimal,
    Context,
    localcontext,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_DOWN,
    ROUND_UP,
    ROUND_05UP,
)

# Summary: Generate finite Decimal operands with varied signs, signed zeros, coefficient sizes,
# decimal exponents, and explicit edge values; generate contexts with varied precision,
# exponent limits, clamp settings, and rounding modes. Check that fma computes
# self * other + third with exactly one final rounding by comparing it to an exact
# integer-scaled decimal reference rounded under the same context.
@given(st.data())
def test_decimal_Decimal_fma(data):
    def decimal_strategy():
        edge_values = st.sampled_from(
            [
                Decimal("0"),
                Decimal("-0"),
                Decimal("1"),
                Decimal("-1"),
                Decimal("10"),
                Decimal("-10"),
                Decimal("0.1"),
                Decimal("-0.1"),
                Decimal("1E-20"),
                Decimal("-1E-20"),
                Decimal("1E+20"),
                Decimal("-1E+20"),
                Decimal("999999999999"),
                Decimal("-999999999999"),
            ]
        )

        tuple_values = st.builds(
            lambda sign, coeff, exp: Decimal(
                (
                    int(sign),
                    tuple(int(ch) for ch in str(abs(coeff))) if coeff else (0,),
                    exp,
                )
            ),
            sign=st.booleans(),
            coeff=st.integers(min_value=0, max_value=10**12),
            exp=st.one_of(
                st.integers(min_value=-20, max_value=20),
                st.sampled_from([-100, -50, -10, -1, 0, 1, 10, 50, 100]),
            ),
        )

        return st.one_of(edge_values, tuple_values)

    def decimal_to_int_and_exp(value):
        parts = value.as_tuple()
        coeff = int("".join(str(digit) for digit in parts.digits))
        if parts.sign:
            coeff = -coeff
        return coeff, parts.exponent

    def exact_fma_rounded(left, right, third, ctx):
        left_int, left_exp = decimal_to_int_and_exp(left)
        right_int, right_exp = decimal_to_int_and_exp(right)
        third_int, third_exp = decimal_to_int_and_exp(third)

        product_int = left_int * right_int
        product_exp = left_exp + right_exp

        common_exp = min(product_exp, third_exp)
        exact_int = (
            product_int * (10 ** (product_exp - common_exp))
            + third_int * (10 ** (third_exp - common_exp))
        )

        sign = int(exact_int < 0)
        digits = tuple(int(ch) for ch in str(abs(exact_int))) if exact_int else (0,)
        exact = Decimal((sign, digits, common_exp))

        reference_context = ctx.copy()
        with localcontext(reference_context):
            return +exact

    rounding = data.draw(
        st.sampled_from(
            [
                ROUND_CEILING,
                ROUND_FLOOR,
                ROUND_HALF_DOWN,
                ROUND_HALF_EVEN,
                ROUND_HALF_UP,
                ROUND_DOWN,
                ROUND_UP,
                ROUND_05UP,
            ]
        )
    )

    ctx = Context(
        prec=data.draw(st.integers(min_value=1, max_value=50)),
        rounding=rounding,
        Emin=data.draw(st.integers(min_value=-50, max_value=0)),
        Emax=data.draw(st.integers(min_value=0, max_value=50)),
        clamp=data.draw(st.booleans()),
    )
    for signal in ctx.traps:
        ctx.traps[signal] = False

    left = data.draw(decimal_strategy())
    right = data.draw(decimal_strategy())
    third = data.draw(decimal_strategy())
    use_explicit_context = data.draw(st.booleans())

    expected = exact_fma_rounded(left, right, third, ctx)

    with localcontext(ctx) as active_context:
        if use_explicit_context:
            actual = left.fma(right, third, context=active_context)
        else:
            actual = left.fma(right, third)

    assert actual == expected
# End program