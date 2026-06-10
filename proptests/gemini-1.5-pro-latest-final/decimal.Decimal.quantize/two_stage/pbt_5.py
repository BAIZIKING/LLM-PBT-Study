from hypothesis import given, strategies as st
import decimal

# Define strategies for Decimal inputs and rounding modes
decimal_strategy = st.decimals(
    min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False
)  # Avoid extremes
rounding_modes = st.sampled_from(
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
)

@given(d1=decimal_strategy, d2=decimal_strategy, rounding=rounding_modes)
def test_decimal_quantize_exponent_match(d1, d2, rounding):
    """Property 1: Exponent of result matches exp argument."""
    result = d1.quantize(d2, rounding=rounding)
    assert result.as_tuple().exponent == d2.as_tuple().exponent

@given(d1=decimal_strategy, d2=decimal_strategy, rounding=rounding_modes)
def test_decimal_quantize_coefficient_length(d1, d2, rounding):
    """Property 2: Coefficient length doesn't exceed precision."""
    result = d1.quantize(d2, rounding=rounding)
    assert len(result.as_tuple().digits) <= decimal.getcontext().prec

@given(d1=decimal_strategy, d2=decimal_strategy)
def test_decimal_quantize_no_underflow(d1, d2):
    """Property 3: No Underflow error, even for subnormal results."""
    try:
        d1.quantize(d2)
    except decimal.Underflow:
        assert False, "Underflow error raised unexpectedly."

@given(
    d1=decimal_strategy,
    d2=decimal_strategy,
    rounding=rounding_modes,
    context=st.builds(decimal.Context, rounding=rounding_modes),
)
def test_decimal_quantize_rounding_behavior(d1, d2, rounding, context):
    """Property 4: Rounding behavior follows specified mode."""
    result1 = d1.quantize(d2, rounding=rounding)
    result2 = d1.quantize(d2, context=context)
    # Compare rounding behavior based on exponents and digits
    assert (
        result1.as_tuple().exponent,
        result1.as_tuple().digits,
    ) == (
        result2.as_tuple().exponent,
        result2.as_tuple().digits,
    )

@given(d1=decimal_strategy, exp=st.integers(min_value=-1000, max_value=1000))
def test_decimal_quantize_error_conditions(d1, exp):
    """Property 5: InvalidOperation for exponents outside allowed range."""
    with pytest.raises(decimal.InvalidOperation):
        d1.quantize(decimal.Decimal(10) ** exp)  # Create Decimal from exponent
# End program