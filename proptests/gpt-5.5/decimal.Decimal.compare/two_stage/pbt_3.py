from hypothesis import given, strategies as st
import decimal


@st.composite
def finite_decimal_values(draw):
    coefficient = draw(st.integers(min_value=0, max_value=10**30))
    exponent = draw(st.integers(min_value=-30, max_value=30))
    value = decimal.Decimal(coefficient).scaleb(exponent)

    if draw(st.booleans()):
        value = -value

    return value


non_nan_decimal_values = st.one_of(
    finite_decimal_values(),
    st.sampled_from([
        decimal.Decimal("Infinity"),
        decimal.Decimal("-Infinity"),
    ]),
)

decimal_values = st.one_of(
    non_nan_decimal_values,
    st.just(decimal.Decimal("NaN")),
)


@given(st.data())
def test_decimal_Decimal_compare_result_is_decimal_property(data):
    a = data.draw(decimal_values)
    b = data.draw(decimal_values)

    result = a.compare(b)

    assert isinstance(result, decimal.Decimal)


@given(st.data())
def test_decimal_Decimal_compare_nan_operand_returns_nan_property(data):
    if data.draw(st.booleans()):
        a = decimal.Decimal("NaN")
        b = data.draw(decimal_values)
    else:
        a = data.draw(decimal_values)
        b = decimal.Decimal("NaN")

    result = a.compare(b)

    assert result.is_nan()


@given(st.data())
def test_decimal_Decimal_compare_non_nan_result_domain_property(data):
    a = data.draw(non_nan_decimal_values)
    b = data.draw(non_nan_decimal_values)

    result = a.compare(b)

    assert result in {
        decimal.Decimal("-1"),
        decimal.Decimal("0"),
        decimal.Decimal("1"),
    }


@given(st.data())
def test_decimal_Decimal_compare_matches_numeric_ordering_property(data):
    a = data.draw(non_nan_decimal_values)
    b = data.draw(non_nan_decimal_values)

    result = a.compare(b)

    if a < b:
        assert result == decimal.Decimal("-1")
    elif a == b:
        assert result == decimal.Decimal("0")
    else:
        assert result == decimal.Decimal("1")


@given(st.data())
def test_decimal_Decimal_compare_reversing_operands_negates_result_property(data):
    a = data.draw(non_nan_decimal_values)
    b = data.draw(non_nan_decimal_values)

    forward = a.compare(b)
    reverse = b.compare(a)

    assert forward == -reverse


# End program