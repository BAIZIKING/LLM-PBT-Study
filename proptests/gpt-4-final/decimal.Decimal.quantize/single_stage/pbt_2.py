from hypothesis import given, strategies as st
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, ROUND_CEILING

# Summary: Generate two decimal values and a rounding mode. Validate until a quantize operation can be performed. 
# In the test, check if the result matches expected behavior based on rounding mode and/or exponent of result.  
@given(st.tuples(st.decimals(min_value=-1e50, max_value=1e50), 
                 st.decimals(min_value=-1e10, max_value=1e10), 
                 st.sampled_from([None, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, ROUND_CEILING])))
def test_decimal_quantize(data):
    number, quantize_to, rounding = data
    
    # We need to ensure that the operation is possible, 
    # as hypothesis isn't aware of the constraints required for a quantize operation. 
    if quantize_to > number:
        return

    result = number.quantize(quantize_to, rounding)
    
    # Returned outcomes validation
    assert isinstance(result, Decimal)
    assert abs(result) <= abs(number)
    assert Decimal(result.as_tuple().exponent) == Decimal(quantize_to.as_tuple().exponent)
# End program