from hypothesis import given, strategies as st
import decimal

@given(st.data())
def test_decimal_Decimal_from_float_returns_decimal_instance(data):
    value = data.draw(
        st.one_of(
            st.integers(min_value=-(10**100), max_value=10**100),
            st.floats(width=64, allow_nan=True, allow_infinity=True),
        )
    )

    result = decimal.Decimal.from_float(value)

    assert isinstance(result, decimal.Decimal)


@given(st.data())
def test_decimal_Decimal_from_float_ints_are_exact(data):
    value = data.draw(st.integers(min_value=-(10**100), max_value=10**100))

    result = decimal.Decimal.from_float(value)

    assert result == decimal.Decimal(value)


@given(st.data())
def test_decimal_Decimal_from_float_finite_floats_are_exact_binary_values(data):
    value = data.draw(st.floats(width=64, allow_nan=False, allow_infinity=False))

    numerator, denominator = value.as_integer_ratio()
    power_of_two = denominator.bit_length() - 1
    expected = decimal.Decimal(numerator * (5 ** power_of_two)).scaleb(-power_of_two)

    result = decimal.Decimal.from_float(value)

    assert result == expected


@given(st.data())
def test_decimal_Decimal_from_float_finite_floats_round_trip_to_same_float(data):
    value = data.draw(st.floats(width=64, allow_nan=False, allow_infinity=False))

    result = decimal.Decimal.from_float(value)

    assert float(result).hex() == value.hex()


@given(st.data())
def test_decimal_Decimal_from_float_preserves_special_float_values(data):
    value = data.draw(
        st.sampled_from(
            [
                float("nan"),
                float("inf"),
                float("-inf"),
            ]
        )
    )

    result = decimal.Decimal.from_float(value)

    if value != value:
        assert result.is_nan()
    elif value == float("inf"):
        assert result == decimal.Decimal("Infinity")
    else:
        assert result == decimal.Decimal("-Infinity")
# End program