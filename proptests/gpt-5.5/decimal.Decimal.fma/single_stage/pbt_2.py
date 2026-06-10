from hypothesis import given, strategies as st
from decimal import (
    Decimal,
    Context,
    localcontext,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    ROUND_05UP,
)

# Summary: Generate finite Decimal operands including signed zeros, small constants, large coefficients,
# varied signs, and varied exponents; generate Decimal contexts with different precisions, exponent
# limits, clamp settings, and rounding modes with traps disabled. Check that fma computes the same
# result as adding the third operand to the exact, unrounded product, rounded only once by the context.
@given(st.data())
def test_decimal_Decimal_fma(data):
    def make_decimal(sign, coefficient, exponent):
        digits = (0,) if coefficient == 0 else tuple(map(int, str(coefficient)))
        return Decimal((int(sign), digits, exponent))

    edge_decimals = st.sampled_from(
        [
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("-1"),
            Decimal("10"),
            Decimal("-10"),
            Decimal("0.1"),
            Decimal("-0.1"),
            Decimal("1E-30"),
            Decimal("-1E-30"),
            Decimal("1E+30"),
            Decimal("-1E+30"),
            Decimal("999999999999999999999999999999"),
            Decimal("-999999999999999999999999999999"),
        ]
    )

    generated_decimals = st.builds(
        make_decimal,
        sign=st.booleans(),
        coefficient=st.integers(min_value=0, max_value=10**30 - 1),
        exponent=st.integers(min_value=-60, max_value=60),
    )

    decimal_values = st.one_of(edge_decimals, generated_decimals)

    self_value = data.draw(decimal_values, label="self")
    other = data.draw(decimal_values, label="other")
    third = data.draw(decimal_values, label="third")

    rounding = data.draw(
        st.sampled_from(
            [
                ROUND_CEILING,
                ROUND_DOWN,
                ROUND_FLOOR,
                ROUND_HALF_DOWN,
                ROUND_HALF_EVEN,
                ROUND_HALF_UP,
                ROUND_UP,
                ROUND_05UP,
            ]
        ),
        label="rounding",
    )

    context = Context(
        prec=data.draw(st.integers(min_value=1, max_value=30), label="precision"),
        rounding=rounding,
        Emin=data.draw(st.integers(min_value=-60, max_value=0), label="Emin"),
        Emax=data.draw(st.integers(min_value=0, max_value=60), label="Emax"),
        clamp=data.draw(st.integers(min_value=0, max_value=1), label="clamp"),
    )
    for signal in context.traps:
        context.traps[signal] = False

    def exact_product(x, y):
        x_tuple = x.as_tuple()
        y_tuple = y.as_tuple()

        x_coeff = int("".join(map(str, x_tuple.digits)))
        y_coeff = int("".join(map(str, y_tuple.digits)))

        product_coeff = x_coeff * y_coeff
        product_sign = x_tuple.sign ^ y_tuple.sign
        product_exponent = x_tuple.exponent + y_tuple.exponent
        product_digits = (0,) if product_coeff == 0 else tuple(map(int, str(product_coeff)))

        return Decimal((product_sign, product_digits, product_exponent))

    product_without_intermediate_rounding = exact_product(self_value, other)

    reference_context = context.copy()
    reference_context.clear_flags()
    expected = reference_context.add(product_without_intermediate_rounding, third)
    expected_flags = dict(reference_context.flags)

    use_explicit_context = data.draw(st.booleans(), label="use_explicit_context")

    if use_explicit_context:
        actual_context = context.copy()
        actual_context.clear_flags()
        actual = self_value.fma(other, third, context=actual_context)
        actual_flags = dict(actual_context.flags)
    else:
        with localcontext(context) as actual_context:
            actual_context.clear_flags()
            actual = self_value.fma(other, third)
            actual_flags = dict(actual_context.flags)

    assert actual.compare_total(expected) == Decimal("0")
    assert actual_flags == expected_flags
# End program