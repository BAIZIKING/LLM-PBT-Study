from hypothesis import given, strategies as st
import decimal

@given(st.data())
def test_decimal_Decimal_from_float_returns_decimal_instance(data):
    value = data.draw(
        st.one_of(
            st.integers(min_value=-(10**100), max_value=10**100),
            st.floats(allow_nan=True, allow_infinity=True, width=64),
        )
    )

    result = decimal.Decimal.from_float(value)

    assert isinstance(result, decimal.Decimal)


@given(st.data())
def test_decimal_Decimal_from_float_integer_inputs_are_exact(data):
    value = data.draw(st.integers(min_value=-(10**100), max_value=10**100))

    result = decimal.Decimal.from_float(value)

    assert result == decimal.Decimal(value)


@given(st.data())
def test_decimal_Decimal_from_float_finite_float_inputs_are_exact(data):
    value = data.draw(st.floats(allow_nan=False, allow_infinity=False, width=64))

    result = decimal.Decimal.from_float(value)

    assert result.as_integer_ratio() == value.as_integer_ratio()


@given(st.data())
def test_decimal_Decimal_from_float_infinity_inputs_preserve_sign(data):
    value = data.draw(st.sampled_from([float("inf"), float("-inf")]))

    result = decimal.Decimal.from_float(value)

    assert result.is_infinite()
    assert result.is_signed() == (value < 0)


@given(st.data())
def test_decimal_Decimal_from_float_nan_inputs_return_decimal_nan(data):
    value = data.draw(st.just(float("nan")))

    result = decimal.Decimal.from_float(value)

    assert result.is_nan()
# End program