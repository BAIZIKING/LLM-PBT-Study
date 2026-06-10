from hypothesis import given, strategies as st
from decimal import (
    Decimal,
    Context,
    localcontext,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_DOWN,
    ROUND_UP,
    ROUND_HALF_EVEN,
    ROUND_HALF_DOWN,
    ROUND_HALF_UP,
    ROUND_05UP,
)

# Summary: Generate finite Decimal operands from both hand-picked edge cases and bounded random coefficients/exponents, sometimes using ints for `other` and `third` as in the docs. Generate varied precisions, rounding modes, and both explicit contexts and implicit current-context use. Check that fma computes `self * other + third` with the multiplication done exactly, then rounded only once by the target context.
@given(st.data())
def test_decimal_Decimal_fma(data):
    decimal_edges = st.sampled_from(
        [
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("-1"),
            Decimal("10"),
            Decimal("-10"),
            Decimal("1E-40"),
            Decimal("-1E-40"),
            Decimal("1E+40"),
            Decimal("-1E+40"),
            Decimal("9999999999999999999999999E-40"),
            Decimal("-9999999999999999999999999E-40"),
            Decimal("9999999999999999999999999E+40"),
            Decimal("-9999999999999999999999999E+40"),
            Decimal("1.0000000000000000000000001"),
            Decimal("-1.0000000000000000000000001"),
        ]
    )

    random_decimal = st.builds(
        lambda coefficient, exponent: Decimal(f"{coefficient}e{exponent}"),
        st.integers(-(10**25), 10**25),
        st.integers(-40, 40),
    )

    decimal_operand = st.one_of(decimal_edges, random_decimal)

    int_operand = st.one_of(
        st.sampled_from([0, 1, -1, 10, -10, 10**25, -(10**25)]),
        st.integers(-(10**25), 10**25),
    )

    mixed_operand = st.one_of(decimal_operand, int_operand)

    self_value = data.draw(decimal_operand)
    other = data.draw(mixed_operand)
    third = data.draw(mixed_operand)

    precision = data.draw(st.integers(1, 35))
    rounding = data.draw(
        st.sampled_from(
            [
                ROUND_CEILING,
                ROUND_FLOOR,
                ROUND_DOWN,
                ROUND_UP,
                ROUND_HALF_EVEN,
                ROUND_HALF_DOWN,
                ROUND_HALF_UP,
                ROUND_05UP,
            ]
        )
    )
    context = Context(
        prec=precision,
        rounding=rounding,
        Emin=-999999,
        Emax=999999,
    )

    use_implicit_context = data.draw(st.booleans())

    def as_decimal(value):
        return value if isinstance(value, Decimal) else Decimal(value)

    other_decimal = as_decimal(other)
    third_decimal = as_decimal(third)

    # Compute the oracle by making the intermediate product exact, then applying
    # the target context once to the final sum.
    exact_context = Context(prec=300, Emin=-999999, Emax=999999)
    with localcontext(exact_context):
        exact_sum = self_value * other_decimal + third_decimal

    if use_implicit_context:
        with localcontext(context):
            result = self_value.fma(other, third)
            expected = +exact_sum
    else:
        result = self_value.fma(other, third, context=context)
        expected = context.plus(exact_sum)

    assert result == expected

# End program