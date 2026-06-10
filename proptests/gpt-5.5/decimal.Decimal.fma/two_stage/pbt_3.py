from hypothesis import given, strategies as st
import decimal

ROUNDINGS = [
    decimal.ROUND_CEILING,
    decimal.ROUND_FLOOR,
    decimal.ROUND_UP,
    decimal.ROUND_DOWN,
    decimal.ROUND_HALF_UP,
    decimal.ROUND_HALF_DOWN,
    decimal.ROUND_HALF_EVEN,
    decimal.ROUND_05UP,
]

BOUNDED_DECIMALS = st.decimals(
    min_value=decimal.Decimal("-1000"),
    max_value=decimal.Decimal("1000"),
    places=3,
    allow_nan=False,
    allow_infinity=False,
)

BOUNDED_INTEGER_DECIMALS = st.integers(
    min_value=-100,
    max_value=100,
).map(decimal.Decimal)


def make_context(prec, rounding):
    return decimal.Context(
        prec=prec,
        rounding=rounding,
        Emin=-50,
        Emax=50,
    )


def exact_fma_value(a, b, c):
    with decimal.localcontext() as ctx:
        ctx.prec = 80
        ctx.Emin = -999999
        ctx.Emax = 999999
        return a * b + c


@given(st.data())
def test_decimal_Decimal_fma_matches_single_rounded_exact_product_plus_third(data):
    a = data.draw(BOUNDED_DECIMALS)
    b = data.draw(BOUNDED_DECIMALS)
    c = data.draw(BOUNDED_DECIMALS)
    prec = data.draw(st.integers(min_value=1, max_value=30))
    rounding = data.draw(st.sampled_from(ROUNDINGS))

    ctx = make_context(prec, rounding)
    exact = exact_fma_value(a, b, c)
    expected = ctx.plus(exact)

    actual = a.fma(b, c, context=make_context(prec, rounding))

    assert actual == expected


@given(st.data())
def test_decimal_Decimal_fma_is_symmetric_in_the_two_multiplicands(data):
    a = data.draw(BOUNDED_DECIMALS)
    b = data.draw(BOUNDED_DECIMALS)
    c = data.draw(BOUNDED_DECIMALS)
    prec = data.draw(st.integers(min_value=1, max_value=30))
    rounding = data.draw(st.sampled_from(ROUNDINGS))

    left = a.fma(b, c, context=make_context(prec, rounding))
    right = b.fma(a, c, context=make_context(prec, rounding))

    assert left == right


@given(st.data())
def test_decimal_Decimal_fma_with_zero_multiplicand_equals_rounded_third_argument(data):
    zero = data.draw(st.sampled_from([decimal.Decimal("0"), decimal.Decimal("-0")]))
    other = data.draw(BOUNDED_DECIMALS)
    third = data.draw(BOUNDED_DECIMALS)
    prec = data.draw(st.integers(min_value=1, max_value=30))
    rounding = data.draw(st.sampled_from(ROUNDINGS))

    ctx = make_context(prec, rounding)
    expected = ctx.plus(third)

    actual = zero.fma(other, third, context=make_context(prec, rounding))

    assert actual == expected


@given(st.data())
def test_decimal_Decimal_fma_with_zero_third_argument_equals_rounded_exact_product(data):
    a = data.draw(BOUNDED_DECIMALS)
    b = data.draw(BOUNDED_DECIMALS)
    zero = decimal.Decimal("0")
    prec = data.draw(st.integers(min_value=1, max_value=30))
    rounding = data.draw(st.sampled_from(ROUNDINGS))

    with decimal.localcontext() as exact_ctx:
        exact_ctx.prec = 80
        exact_ctx.Emin = -999999
        exact_ctx.Emax = 999999
        exact_product = a * b

    ctx = make_context(prec, rounding)
    expected = ctx.plus(exact_product)

    actual = a.fma(b, zero, context=make_context(prec, rounding))

    assert actual == expected


@given(st.data())
def test_decimal_Decimal_fma_returns_exact_value_when_representable_in_context(data):
    a = data.draw(BOUNDED_INTEGER_DECIMALS)
    b = data.draw(BOUNDED_INTEGER_DECIMALS)
    c = data.draw(BOUNDED_INTEGER_DECIMALS)
    rounding = data.draw(st.sampled_from(ROUNDINGS))

    ctx = make_context(prec=10, rounding=rounding)
    expected = exact_fma_value(a, b, c)

    actual = a.fma(b, c, context=ctx)

    assert actual == expected

# End program