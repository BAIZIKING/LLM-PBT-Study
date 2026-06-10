from hypothesis import given, strategies as st
import decimal


ROUNDING_MODES = [
    decimal.ROUND_CEILING,
    decimal.ROUND_FLOOR,
    decimal.ROUND_UP,
    decimal.ROUND_DOWN,
    decimal.ROUND_HALF_UP,
    decimal.ROUND_HALF_DOWN,
    decimal.ROUND_HALF_EVEN,
]


def finite_decimal_strategy(max_digits=12, min_exponent=-12, max_exponent=12):
    return st.builds(
        lambda sign, digits, exponent: decimal.Decimal((sign, tuple(digits), exponent)),
        st.integers(min_value=0, max_value=1),
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=max_digits),
        st.integers(min_value=min_exponent, max_value=max_exponent),
    )


def coefficient_as_int(value):
    result = 0
    for digit in value.as_tuple().digits:
        result = result * 10 + digit
    return result


def digits_from_int(value):
    if value == 0:
        return (0,)
    return tuple(int(ch) for ch in str(value))


@given(st.data())
def test_decimal_Decimal_quantize_result_has_exponent_of_second_operand(data):
    x = data.draw(finite_decimal_strategy(max_digits=12, min_exponent=-12, max_exponent=12))
    target_exponent = data.draw(st.integers(min_value=-12, max_value=12))
    rounding = data.draw(st.sampled_from(ROUNDING_MODES))

    quantizer = decimal.Decimal((0, (1,), target_exponent))
    context = decimal.Context(prec=50, Emin=-100, Emax=100, rounding=rounding)

    result = x.quantize(quantizer, context=context)

    assert result.as_tuple().exponent == quantizer.as_tuple().exponent


@given(st.data())
def test_decimal_Decimal_quantize_round_down_matches_truncation_to_target_exponent(data):
    x = data.draw(finite_decimal_strategy(max_digits=8, min_exponent=-6, max_exponent=6))
    target_exponent = data.draw(st.integers(min_value=-6, max_value=6))

    quantizer = decimal.Decimal((0, (1,), target_exponent))
    context = decimal.Context(
        prec=30,
        Emin=-100,
        Emax=100,
        rounding=decimal.ROUND_DOWN,
    )

    result = x.quantize(quantizer, context=context)

    sign = x.as_tuple().sign
    coefficient = coefficient_as_int(x)
    exponent_difference = x.as_tuple().exponent - target_exponent

    if exponent_difference >= 0:
        expected_coefficient = coefficient * (10 ** exponent_difference)
    else:
        expected_coefficient = coefficient // (10 ** (-exponent_difference))

    expected = decimal.Decimal(
        (sign, digits_from_int(expected_coefficient), target_exponent)
    )

    assert result == expected
    assert result.as_tuple().exponent == target_exponent


@given(st.data())
def test_decimal_Decimal_quantize_without_required_rounding_preserves_numeric_value(data):
    exponent = data.draw(st.integers(min_value=-12, max_value=12))
    x = data.draw(finite_decimal_strategy(max_digits=12, min_exponent=exponent, max_exponent=exponent))

    quantizer = decimal.Decimal((0, (1,), exponent))
    context = decimal.Context(prec=50, Emin=-100, Emax=100)

    result = x.quantize(quantizer, context=context)

    assert result == x
    assert result.as_tuple().exponent == exponent


@given(st.data())
def test_decimal_Decimal_quantize_signals_invalid_operation_when_result_coefficient_exceeds_precision(data):
    precision = data.draw(st.integers(min_value=1, max_value=8))
    exponent = data.draw(st.integers(min_value=-5, max_value=5))
    first_digit = data.draw(st.integers(min_value=1, max_value=9))
    remaining_digits = data.draw(
        st.lists(
            st.integers(min_value=0, max_value=9),
            min_size=precision,
            max_size=precision,
        )
    )

    digits = (first_digit, *remaining_digits)
    x = decimal.Decimal((0, digits, exponent))
    quantizer = decimal.Decimal((0, (1,), exponent))

    context = decimal.Context(prec=precision, Emin=-100, Emax=100)
    context.traps[decimal.InvalidOperation] = True

    try:
        x.quantize(quantizer, context=context)
    except decimal.InvalidOperation:
        pass
    else:
        assert False, "quantize should signal InvalidOperation when coefficient length exceeds precision"


@given(st.data())
def test_decimal_Decimal_quantize_never_signals_underflow_for_subnormal_inexact_result(data):
    precision = data.draw(st.integers(min_value=2, max_value=8))
    emin = data.draw(st.integers(min_value=-30, max_value=-2))

    context = decimal.Context(
        prec=precision,
        Emin=emin,
        Emax=30,
        rounding=decimal.ROUND_DOWN,
    )
    context.traps[decimal.Underflow] = True
    context.traps[decimal.Inexact] = False
    context.traps[decimal.Rounded] = False
    context.clear_flags()

    target_exponent = context.Etiny()
    x = decimal.Decimal((0, (1, 4), target_exponent - 1))
    quantizer = decimal.Decimal((0, (1,), target_exponent))

    result = x.quantize(quantizer, context=context)

    assert result.as_tuple().exponent == target_exponent
    assert result.is_subnormal(context=context)
    assert context.flags[decimal.Inexact]
    assert context.flags[decimal.Rounded]
    assert not context.flags[decimal.Underflow]


# End program