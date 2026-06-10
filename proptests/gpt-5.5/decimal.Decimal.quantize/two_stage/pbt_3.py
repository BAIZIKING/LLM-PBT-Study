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
    decimal.ROUND_05UP,
]


def _decimal_from_parts(sign, coefficient, exponent):
    digits = (0,) if coefficient == 0 else tuple(int(ch) for ch in str(coefficient))
    return decimal.Decimal((sign, digits, exponent))


def _quantum(exponent):
    return decimal.Decimal((0, (1,), exponent))


def _disable_all_traps(context):
    for signal in context.traps:
        context.traps[signal] = False


def _expected_one_decimal_round_to_integer(sign, whole, tenth, rounding):
    if tenth == 0:
        magnitude = whole
    elif rounding == decimal.ROUND_DOWN:
        magnitude = whole
    elif rounding == decimal.ROUND_UP:
        magnitude = whole + 1
    elif rounding == decimal.ROUND_CEILING:
        magnitude = whole + 1 if sign == 0 else whole
    elif rounding == decimal.ROUND_FLOOR:
        magnitude = whole + 1 if sign == 1 else whole
    elif rounding == decimal.ROUND_HALF_UP:
        magnitude = whole + 1 if tenth >= 5 else whole
    elif rounding == decimal.ROUND_HALF_DOWN:
        magnitude = whole + 1 if tenth > 5 else whole
    elif rounding == decimal.ROUND_HALF_EVEN:
        if tenth > 5:
            magnitude = whole + 1
        elif tenth < 5:
            magnitude = whole
        else:
            magnitude = whole if whole % 2 == 0 else whole + 1
    elif rounding == decimal.ROUND_05UP:
        magnitude = whole + 1 if whole % 10 in (0, 5) else whole
    else:
        raise AssertionError("Unexpected rounding mode")

    return decimal.Decimal(-magnitude if sign else magnitude)


@given(st.data())
def test_decimal_Decimal_quantize_exponent_matches_quantum_property(data):
    sign = data.draw(st.integers(min_value=0, max_value=1))
    coefficient = data.draw(st.integers(min_value=0, max_value=999999))
    operand_exponent = data.draw(st.integers(min_value=-6, max_value=6))
    quantum_exponent = data.draw(st.integers(min_value=-6, max_value=6))

    operand = _decimal_from_parts(sign, coefficient, operand_exponent)
    quantum = _quantum(quantum_exponent)

    context = decimal.Context(
        prec=50,
        rounding=decimal.ROUND_HALF_EVEN,
        Emin=-100,
        Emax=100,
    )

    result = operand.quantize(quantum, context=context)

    assert result.as_tuple().exponent == quantum_exponent


@given(st.data())
def test_decimal_Decimal_quantize_explicit_rounding_mode_property(data):
    sign = data.draw(st.integers(min_value=0, max_value=1))
    whole = data.draw(st.integers(min_value=0, max_value=1000))
    tenth = data.draw(st.integers(min_value=0, max_value=9))
    rounding = data.draw(st.sampled_from(ROUNDING_MODES))
    context_rounding = data.draw(st.sampled_from(ROUNDING_MODES))

    coefficient = whole * 10 + tenth
    operand = _decimal_from_parts(sign, coefficient, -1)
    quantum = decimal.Decimal("1")

    context = decimal.Context(
        prec=20,
        rounding=context_rounding,
        Emin=-100,
        Emax=100,
    )

    result = operand.quantize(quantum, rounding=rounding, context=context)
    expected = _expected_one_decimal_round_to_integer(sign, whole, tenth, rounding)

    assert result == expected
    assert result.as_tuple().exponent == quantum.as_tuple().exponent


@given(st.data())
def test_decimal_Decimal_quantize_coefficient_longer_than_precision_property(data):
    precision = data.draw(st.integers(min_value=1, max_value=9))
    coefficient = data.draw(
        st.integers(
            min_value=10**precision,
            max_value=(10 ** (precision + 1)) - 1,
        )
    )

    operand = _decimal_from_parts(0, coefficient, 0)
    quantum = decimal.Decimal("1")

    context = decimal.Context(
        prec=precision,
        rounding=decimal.ROUND_HALF_EVEN,
        Emin=-100,
        Emax=100,
    )
    _disable_all_traps(context)
    context.traps[decimal.InvalidOperation] = True

    try:
        operand.quantize(quantum, context=context)
    except decimal.InvalidOperation:
        pass
    else:
        assert False, "quantize should signal InvalidOperation when coefficient length exceeds precision"


@given(st.data())
def test_decimal_Decimal_quantize_never_signals_underflow_property(data):
    sign = data.draw(st.integers(min_value=0, max_value=1))
    discarded_digit = data.draw(st.integers(min_value=1, max_value=9))
    rounding = data.draw(st.sampled_from(ROUNDING_MODES))

    operand = _decimal_from_parts(sign, 10 + discarded_digit, -4)
    quantum = decimal.Decimal("0.001")

    context = decimal.Context(
        prec=2,
        rounding=rounding,
        Emin=-2,
        Emax=9,
    )
    _disable_all_traps(context)
    context.traps[decimal.Underflow] = True
    context.clear_flags()

    result = operand.quantize(quantum, rounding=rounding, context=context)

    assert result.as_tuple().exponent == quantum.as_tuple().exponent
    assert not context.flags[decimal.Underflow]


@given(st.data())
def test_decimal_Decimal_quantize_exponent_outside_context_bounds_property(data):
    precision = data.draw(st.integers(min_value=1, max_value=6))
    emin = data.draw(st.integers(min_value=-10, max_value=-1))
    emax = data.draw(st.integers(min_value=0, max_value=10))
    use_upper_bound = data.draw(st.booleans())

    context = decimal.Context(
        prec=precision,
        rounding=decimal.ROUND_HALF_EVEN,
        Emin=emin,
        Emax=emax,
    )
    _disable_all_traps(context)
    context.traps[decimal.InvalidOperation] = True

    invalid_exponent = emax + 1 if use_upper_bound else context.Etiny() - 1

    operand = decimal.Decimal("1")
    quantum = _quantum(invalid_exponent)

    try:
        operand.quantize(quantum, context=context)
    except decimal.InvalidOperation:
        pass
    else:
        assert False, "quantize should signal InvalidOperation when result exponent is outside context bounds"


# End program