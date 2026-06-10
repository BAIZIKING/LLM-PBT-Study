from hypothesis import given, strategies as st
import decimal

_DECIMALS = st.decimals(
    min_value=decimal.Decimal("-1000000"),
    max_value=decimal.Decimal("1000000"),
    places=6,
    allow_nan=False,
    allow_infinity=False,
)

_ROUNDINGS = st.sampled_from([
    decimal.ROUND_CEILING,
    decimal.ROUND_FLOOR,
    decimal.ROUND_UP,
    decimal.ROUND_DOWN,
    decimal.ROUND_HALF_UP,
    decimal.ROUND_HALF_DOWN,
    decimal.ROUND_HALF_EVEN,
    decimal.ROUND_05UP,
])

_CONTEXTS = st.builds(
    lambda prec, rounding: decimal.Context(
        prec=prec,
        rounding=rounding,
        Emin=-999,
        Emax=999,
    ),
    st.integers(min_value=1, max_value=50),
    _ROUNDINGS,
)


def _exact_value(x, y, z):
    with decimal.localcontext(decimal.Context(prec=100, Emin=-999999, Emax=999999)):
        return x * y + z


def _rounded_in_context(value, context):
    return context.copy().create_decimal(value)


@given(st.data())
def test_decimal_Decimal_fma_property_correctly_rounded_unrounded_product(data):
    x = data.draw(_DECIMALS)
    y = data.draw(_DECIMALS)
    z = data.draw(_DECIMALS)
    context = data.draw(_CONTEXTS)

    exact = _exact_value(x, y, z)
    expected = _rounded_in_context(exact, context)
    actual = x.fma(y, z, context=context.copy())

    assert actual == expected


@given(st.data())
def test_decimal_Decimal_fma_property_exact_when_representable(data):
    x = data.draw(_DECIMALS)
    y = data.draw(_DECIMALS)
    z = data.draw(_DECIMALS)
    context = decimal.Context(
        prec=60,
        rounding=data.draw(_ROUNDINGS),
        Emin=-999,
        Emax=999,
    )

    exact = _exact_value(x, y, z)
    actual = x.fma(y, z, context=context)

    assert actual == exact


@given(st.data())
def test_decimal_Decimal_fma_property_commutative_multiplicands(data):
    x = data.draw(_DECIMALS)
    y = data.draw(_DECIMALS)
    z = data.draw(_DECIMALS)
    context = data.draw(_CONTEXTS)

    left = x.fma(y, z, context=context.copy())
    right = y.fma(x, z, context=context.copy())

    assert left == right


@given(st.data())
def test_decimal_Decimal_fma_property_zero_third_matches_multiplication(data):
    x = data.draw(_DECIMALS)
    y = data.draw(_DECIMALS)
    context = data.draw(_CONTEXTS)

    actual = x.fma(y, decimal.Decimal(0), context=context.copy())

    with decimal.localcontext(context.copy()):
        expected = x * y

    assert actual == expected


@given(st.data())
def test_decimal_Decimal_fma_property_zero_multiplier_matches_rounded_third(data):
    x = data.draw(_DECIMALS)
    z = data.draw(_DECIMALS)
    context = data.draw(_CONTEXTS)

    actual = x.fma(decimal.Decimal(0), z, context=context.copy())
    expected = _rounded_in_context(z, context)

    assert actual == expected

# End program