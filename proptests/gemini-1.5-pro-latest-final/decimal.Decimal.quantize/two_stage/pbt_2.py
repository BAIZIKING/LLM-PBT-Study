from hypothesis import given, strategies as st
import decimal

# Define strategies for generating Decimal objects and rounding modes
decimals = st.decimals(
    min_value=-1e100,
    max_value=1e100,
    allow_nan=False,
    allow_infinity=False,
    places=10
)
rounding_modes = st.sampled_from(
    [decimal.ROUND_UP, decimal.ROUND_DOWN, decimal.ROUND_CEILING, decimal.ROUND_FLOOR, decimal.ROUND_HALF_UP, decimal.ROUND_HALF_DOWN, decimal.ROUND_HALF_EVEN]
)

@given(decimals, decimals, rounding_modes)
def test_decimal_quantize_exponent_match(x, exp, rounding):
    # Property 1: Exponent Match
    result = x.quantize(exp, rounding=rounding)
    assert result.as_tuple().exponent == exp.as_tuple().exponent

@given(decimals, decimals)
def test_decimal_quantize_coefficient_length(x, exp):
    # Property 2: Coefficient Length
    result = x.quantize(exp)
    assert len(result.as_tuple().digits) <= decimal.getcontext().prec

@given(decimals, decimals, rounding_modes)
def test_decimal_quantize_rounding_behavior(x, exp, rounding):
    # Property 3: Rounding Behavior (comparing with manually rounded value)
    expected_rounded = x.quantize(exp, rounding=rounding).quantize(decimal.Decimal(1), rounding=decimal.ROUND_DOWN)  # Round to nearest integer for comparison
    manual_rounded = decimal.Decimal(int(x.to_integral_value(rounding=rounding))).quantize(exp)
    assert expected_rounded == manual_rounded

@given(decimals, st.decimals(min_value=-1e99, max_value=-1e100, allow_nan=False, allow_infinity=False))
def test_decimal_quantize_exponent_out_of_range(x, exp):
    # Property 4: Error on Exponent Out of Range (expecting InvalidOperation)
    with pytest.raises(decimal.InvalidOperation):
        x.quantize(exp)

@given(decimals, decimals)
def test_decimal_quantize_no_underflow(x, exp):
    # Property 5: No Underflow (checking flags)
    result = x.quantize(exp)
    assert not result.is_subnormal() or not result.is_inexact()

# End program