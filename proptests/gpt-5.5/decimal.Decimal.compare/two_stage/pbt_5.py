from hypothesis import given, strategies as st
import decimal

FINITE_DECIMALS = st.decimals(
    min_value=decimal.Decimal("-1e100"),
    max_value=decimal.Decimal("1e100"),
    places=20,
    allow_nan=False,
    allow_infinity=False,
)

NON_NAN_DECIMALS = st.one_of(
    FINITE_DECIMALS,
    st.sampled_from([decimal.Decimal("-Infinity"), decimal.Decimal("Infinity")]),
)

ANY_DECIMALS = st.one_of(
    NON_NAN_DECIMALS,
    st.just(decimal.Decimal("NaN")),
)


@given(st.data())
def test_decimal_Decimal_compare_result_is_decimal_instance(data):
    a = data.draw(ANY_DECIMALS)
    b = data.draw(ANY_DECIMALS)

    result = a.compare(b)

    assert isinstance(result, decimal.Decimal)


@given(st.data())
def test_decimal_Decimal_compare_nan_operand_returns_nan(data):
    if data.draw(st.booleans()):
        a = decimal.Decimal("NaN")
        b = data.draw(ANY_DECIMALS)
    else:
        a = data.draw(ANY_DECIMALS)
        b = decimal.Decimal("NaN")

    result = a.compare(b)

    assert result.is_nan()


@given(st.data())
def test_decimal_Decimal_compare_non_nan_result_is_minus_one_zero_or_one(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    result = a.compare(b)

    assert result in {
        decimal.Decimal("-1"),
        decimal.Decimal("0"),
        decimal.Decimal("1"),
    }


@given(st.data())
def test_decimal_Decimal_compare_minus_one_exactly_when_less_than(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    result = a.compare(b)

    assert (result == decimal.Decimal("-1")) == (a < b)


@given(st.data())
def test_decimal_Decimal_compare_reverse_order_negates_result(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    forward = a.compare(b)
    reverse = b.compare(a)

    assert forward == -reverse


# End program