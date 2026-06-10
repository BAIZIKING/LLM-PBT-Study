from hypothesis import given, strategies as st
import decimal

FINITE_DECIMALS = st.decimals(
    min_value=decimal.Decimal("-1e100"),
    max_value=decimal.Decimal("1e100"),
    allow_nan=False,
    allow_infinity=False,
    places=20,
)

INFINITE_DECIMALS = st.sampled_from([
    decimal.Decimal("Infinity"),
    decimal.Decimal("-Infinity"),
])

QUIET_NANS = st.sampled_from([
    decimal.Decimal("NaN"),
    decimal.Decimal("-NaN"),
])

NON_NAN_DECIMALS = st.one_of(FINITE_DECIMALS, INFINITE_DECIMALS)
DECIMALS = st.one_of(NON_NAN_DECIMALS, QUIET_NANS)


@given(st.data())
def test_decimal_Decimal_compare_property_result_is_decimal(data):
    a = data.draw(DECIMALS)
    b = data.draw(DECIMALS)

    result = a.compare(b)

    assert isinstance(result, decimal.Decimal)


@given(st.data())
def test_decimal_Decimal_compare_property_nan_operand_gives_nan(data):
    nan_value = data.draw(QUIET_NANS)
    other = data.draw(DECIMALS)

    if data.draw(st.booleans()):
        a, b = nan_value, other
    else:
        a, b = other, nan_value

    result = a.compare(b)

    assert result.is_nan()


@given(st.data())
def test_decimal_Decimal_compare_property_non_nan_result_domain(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    result = a.compare(b)

    assert result in {
        decimal.Decimal("-1"),
        decimal.Decimal("0"),
        decimal.Decimal("1"),
    }


@given(st.data())
def test_decimal_Decimal_compare_property_zero_iff_equal(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    result = a.compare(b)

    assert (result == decimal.Decimal("0")) == (a == b)


@given(st.data())
def test_decimal_Decimal_compare_property_reverse_order_negates(data):
    a = data.draw(NON_NAN_DECIMALS)
    b = data.draw(NON_NAN_DECIMALS)

    forward = a.compare(b)
    backward = b.compare(a)

    assert forward == -backward

# End program