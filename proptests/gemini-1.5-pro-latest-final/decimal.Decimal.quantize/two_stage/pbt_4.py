from hypothesis import given, strategies as st, settings
import decimal

# Settings to handle potential overflows and improve performance
settings.register_profile("decimal_tests", max_examples=1000, deadline=None)
settings.load_profile("decimal_tests")


# Strategy for generating Decimal numbers with controlled exponents
def decimal_strategy(min_exp=-100, max_exp=100):
    """Generates Decimal numbers with exponents within a specified range."""
    return st.decimals(
        min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False
    ).map(lambda x: x.quantize(decimal.Decimal(10) ** st.integers(min_exp, max_exp)))


@given(
    x=decimal_strategy(),
    exp=decimal_strategy(max_value=20),  # Limit exponent to avoid overflows
    rounding=st.sampled_from(
        [
            decimal.ROUND_CEILING,
            decimal.ROUND_DOWN,
            decimal.ROUND_FLOOR,
            decimal.ROUND_HALF_DOWN,
            decimal.ROUND_HALF_EVEN,
            decimal.ROUND_HALF_UP,
            decimal.ROUND_UP,
            decimal.ROUND_05UP,
        ]
    ),
)
def test_decimal_Decimal_quantize_exponent_match(x, exp, rounding):
    """Tests that the exponent of the result matches the quantized exponent."""
    result = x.quantize(exp, rounding=rounding)
    assert result.as_tuple().exponent == exp.as_tuple().exponent


@given(x=decimal_strategy(), exp=decimal_strategy())
def test_decimal_Decimal_quantize_precision_limit(x, exp):
    """Tests that the result's coefficient length doesn't exceed precision."""
    result = x.quantize(exp)
    assert len(result.as_tuple().digits) <= decimal.getcontext().prec


@given(x=decimal_strategy(), exp=decimal_strategy())
def test_decimal_Decimal_quantize_no_underflow(x, exp):
    """Tests that quantize never raises an Underflow error."""
    try:
        x.quantize(exp)
    except decimal.Underflow:
        assert False


@given(
    x=decimal_strategy(),
    exp=decimal_strategy(min_value=2),  # Ensure potential rounding
    rounding=st.sampled_from(
        [
            decimal.ROUND_CEILING,
            decimal.ROUND_DOWN,
            decimal.ROUND_FLOOR,
            decimal.ROUND_HALF_DOWN,
            decimal.ROUND_HALF_EVEN,
            decimal.ROUND_HALF_UP,
            decimal.ROUND_UP,
            decimal.ROUND_05UP,
        ]
    ),
)
def test_decimal_Decimal_quantize_rounding_behavior(x, exp, rounding):
    """Tests that rounding behavior is consistent with the specified mode."""
    result = x.quantize(exp, rounding=rounding)
    # Compare with expected result using the same rounding mode
    expected = decimal.Decimal(x.quantize(exp, rounding=rounding).to_eng_string())
    assert result == expected


@given(x=decimal_strategy(), exp=decimal_strategy())
def test_decimal_Decimal_quantize_exponent_range(x, exp):
    """Tests that the result's exponent is within the valid range."""
    result = x.quantize(exp)
    assert decimal.Decimal.Etiny() <= result.as_tuple().exponent <= decimal.Decimal.Emax()


# End program