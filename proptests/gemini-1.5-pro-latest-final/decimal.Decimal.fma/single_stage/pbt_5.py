from hypothesis import given, strategies as st
import decimal

# Summary: Generate diverse decimal inputs and contexts, ensuring accurate fma calculations and handling of special cases.
@given(st.data())
def test_decimal_Decimal_fma(data):
    # Generate decimals and context
    self_dec = data.draw(st.decimals())
    other_dec = data.draw(st.decimals())
    third_dec = data.draw(st.decimals())
    context = data.draw(st.one_of(st.none(), st.builds(decimal.Context)))

    # Calculate result using fma and regular arithmetic
    fma_result = self_dec.fma(other_dec, third_dec, context=context)
    manual_result = (self_dec * other_dec + third_dec).quantize(decimal.Decimal("1E-28")) 

    # Check for NaN 
    if self_dec.is_nan() or other_dec.is_nan() or third_dec.is_nan():
        assert fma_result.is_nan() 
    # Check for sNaN
    elif self_dec.is_snan() or other_dec.is_snan() or third_dec.is_snan():
        assert fma_result.is_snan()
    # Check for infinities
    elif self_dec.is_infinite() or other_dec.is_infinite() or third_dec.is_infinite():
        # Handle cases with opposing infinities resulting in NaN 
        if (self_dec.is_infinite() and other_dec.is_infinite() and self_dec.copy_sign(other_dec) == decimal.Decimal("-1")) or \
           (self_dec.is_infinite() and third_dec.is_infinite() and self_dec.copy_sign(third_dec) == decimal.Decimal("-1")) or \
           (other_dec.is_infinite() and third_dec.is_infinite() and other_dec.copy_sign(third_dec) == decimal.Decimal("-1")):
            assert fma_result.is_nan()
        else: 
            assert fma_result.is_infinite()
    # Check for normal cases and compare results 
    else:
        assert fma_result == manual_result 
# End program