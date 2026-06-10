from hypothesis import given, strategies as st, settings
import decimal

# Settings to manage potential overflows and improve performance
settings.register_profile("decimal_tests", max_examples=1000, deadline=None)
settings.load_profile("decimal_tests")

# Strategies for generating Decimal numbers and rounding modes
decimals = st.decimals(
    min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
)
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

@given(d1=decimals, d2=decimals, rounding_mode=rounding_modes)
def test_decimal_quantize_exponent_match(d1, d2, rounding_mode):
    # Property 1: Exponent Match
    result = d1.quantize(d2.exp(), rounding=rounding_mode)
    assert result.as_tuple().exponent == d2.as_tuple().exponent
# End program

@given(d1=decimals, d2=decimals)
def test_decimal_quantize_precision_limit(d1, d2):
    # Property 2: Precision Limit
    result = d1.quantize(d2.exp())
    assert len(result.as_tuple().digits) <= decimal.getcontext().prec
# End program

@given(d1=decimals, d2=decimals)
def test_decimal_quantize_no_underflow(d1, d2):
    # Property 3: No Underflow
    try:
        d1.quantize(d2.exp())
    except decimal.Underflow:
        assert False
# End program 

@given(d1=decimals, d2=decimals, rounding_mode=rounding_modes)
def test_decimal_quantize_rounding_behavior(d1, d2, rounding_mode):
    # Property 4: Rounding Behavior - This is complex to assert directly due to various rounding modes and edge cases.
    # Instead, we test for consistency by comparing with the decimal module's rounding function.
    quantized = d1.quantize(d2.exp(), rounding_mode)
    expected = decimal.Decimal(d1.quantize(d2.exp())).quantize(
        decimal.Decimal("1"), rounding=rounding_mode
    )
    assert quantized == expected
# End program

@given(d1=decimals)
def test_decimal_quantize_exponent_out_of_range(d1):
    # Property 5: Error on Exponent Out of Range
    with pytest.raises(decimal.InvalidOperation):
        d1.quantize(decimal.Decimal("1E9999"))  # Exponent exceeding Emax
    with pytest.raises(decimal.InvalidOperation):
        d1.quantize(decimal.Decimal("1E-9999")) # Exponent below Etiny
# End program