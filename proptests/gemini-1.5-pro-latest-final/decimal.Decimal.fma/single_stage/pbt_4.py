from hypothesis import given, strategies as st
from decimal import Decimal, Context

# Summary: Generates a wide range of Decimal inputs including positive, negative, zero, NaN, Infinity, -Infinity values with varying precisions.
@given(st.data())
def test_decimal_fma(data):
    # Generate Decimal inputs with varying signs and magnitudes
    self_dec = data.draw(st.decimals(
        allow_nan=True, allow_infinity=True, allow_subnormal=True, places=10))
    other_dec = data.draw(st.decimals(
        allow_nan=True, allow_infinity=True, allow_subnormal=True, places=5))
    third_dec = data.draw(st.decimals(
        allow_nan=True, allow_infinity=True, allow_subnormal=True, places=8))

    # Create a context with a specific precision for testing
    context = Context(prec=12)

    # Calculate expected result with and without intermediate rounding
    expected_no_rounding = (self_dec * other_dec + third_dec).quantize(Decimal('1E-12'))
    expected_with_rounding = (
        (self_dec * other_dec).quantize(Decimal('1E-12')) + third_dec).quantize(Decimal('1E-12'))

    # Perform fma with the generated inputs and compare with expected results
    result = self_dec.fma(other_dec, third_dec, context=context)
    assert result == expected_no_rounding or result == expected_with_rounding
    
# End program