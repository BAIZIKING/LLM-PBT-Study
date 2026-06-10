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
    ROUND_UP,
    ROUND_DOWN,
    ROUND_05UP,
)

# Summary: Generate finite Decimal operands from targeted edge cases and random signed coefficient/exponent tuples; generate other/third as either Decimals or exact ints; generate varied Decimal contexts with different precision, rounding, exponent bounds, and clamp settings. Check that fma returns self*other+third rounded only once by comparing it with an exact high-precision computation followed by applying the tested context.
@given(st.data())
def test_decimal_Decimal_fma(data):
    edge_decimals = st.sampled_from(
        [
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("-1"),
            Decimal("2"),
            Decimal("-2"),
            Decimal("10"),
            Decimal("-10"),
            Decimal("0.1"),
            Decimal("-0.1"),
            Decimal("1E-50"),
            Decimal("-1E-50"),
            Decimal("9.99999999999999999E+50"),
            Decimal("-9.99999999999999999E+50"),
            Decimal("9.99999999999999999E-50"),
            Decimal("-9.99999999999999999E-50"),
        ]
    )

    random_decimals = st.builds(
        lambda sign, coeff, exp: Decimal(
            (int(sign), tuple(map(int, str(coeff))), exp)
        ),
        st.booleans(),
        st.integers(min_value=0, max_value=10**18 - 1),
        st.integers(min_value=-50, max_value=50),
    )

    finite_decimals = st.one_of(edge_decimals, random_decimals)

    exact_ints = st.one_of(
        st.sampled_from([0, 1, -1, 10, -10, 10**12, -(10**12)]),
        st.integers(min_value=-(10**12), max_value=10**12),
    )

    operand_strategy = st.one_of(finite_decimals, exact_ints)

    self_value = data.draw(finite_decimals, label="self")
    other = data.draw(operand_strategy, label="other")
    third = data.draw(operand_strategy, label="third")

    rounding = data.draw(
        st.sampled_from(
            [
                ROUND_CEILING,
                ROUND_FLOOR,
                ROUND_HALF_DOWN,
                ROUND_HALF_EVEN,
                ROUND_HALF_UP,
                ROUND_UP,
                ROUND_DOWN,
                ROUND_05UP,
            ]
        ),
        label="rounding",
    )

    context = Context(
        prec=data.draw(st.integers(min_value=1, max_value=50), label="precision"),
        rounding=rounding,
        Emin=data.draw(st.integers(min_value=-60, max_value=0), label="Emin"),
        Emax=data.draw(st.integers(min_value=0, max_value=60), label="Emax"),
        clamp=data.draw(st.integers(min_value=0, max_value=1), label="clamp"),
    )

    for signal in context.traps:
        context.traps[signal] = False

    wide_context = Context(
        prec=300,
        rounding=rounding,
        Emin=-999999,
        Emax=999999,
    )

    for signal in wide_context.traps:
        wide_context.traps[signal] = False

    with localcontext(wide_context):
        exact_unrounded_result = self_value * other + third

    expected = context.copy().plus(exact_unrounded_result)

    call_mode = data.draw(
        st.sampled_from(["explicit_context", "implicit_context", "none_context"]),
        label="call_mode",
    )

    if call_mode == "explicit_context":
        actual = self_value.fma(other, third, context=context.copy())
    elif call_mode == "none_context":
        with localcontext(context.copy()):
            actual = self_value.fma(other, third, context=None)
    else:
        with localcontext(context.copy()):
            actual = self_value.fma(other, third)

    assert actual == expected

# End program