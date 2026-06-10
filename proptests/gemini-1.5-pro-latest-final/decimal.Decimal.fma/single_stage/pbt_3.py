from hypothesis import given, strategies as st
from decimal import Decimal, Context

# Summary: Generates diverse Decimal inputs, including edge cases and varying contexts, to test the accuracy and behavior of fma. 
@given(st.data())
def test_decimal_fma(data):
    # Generate Decimal inputs
    self_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    other_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    third_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    
    # Generate context with different rounding options
    context = data.draw(st.sampled_from([
        Context(rounding=rounding) for rounding in [
            'ROUND_CEILING', 'ROUND_DOWN', 'ROUND_FLOOR', 'ROUND_HALF_DOWN',
            'ROUND_HALF_EVEN', 'ROUND_HALF_UP', 'ROUND_UP', 'ROUND_05UP'
        ]
    ]))
    
    # Calculate expected result with controlled rounding
    expected_result = (self_dec * other_dec).quantize(Decimal('1E-28')) + third_dec  
    
    # Test fma with and without context
    result_no_context = Decimal.fma(self_dec, other_dec, third_dec)
    result_with_context = Decimal.fma(self_dec, other_dec, third_dec, context=context)
    
    # Check accuracy 
    assert result_no_context == expected_result
    
    # Check context consistency (if context is provided)
    if context:
        assert result_with_context == expected_result.quantize(Decimal('1E-28'), rounding=context.rounding)

# End Program