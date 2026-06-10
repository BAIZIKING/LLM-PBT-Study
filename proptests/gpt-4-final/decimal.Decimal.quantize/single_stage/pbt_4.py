from hypothesis import given, strategies as st
from random import choice
from decimal import Decimal, ROUND_UP, ROUND_DOWN, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_05UP

rounding_choices = [ROUND_UP, ROUND_DOWN, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_05UP]

@given(st.decimals(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False, places=None), 
       st.decimals(min_value=0, max_value=100, allow_nan=False, allow_infinity=False, places=None), 
       st.data())
def test_decimal_quantize(dec1, dec2, data):
    rounding = data.draw(st.sampled_from(rounding_choices), label='rounding')
    
    # Test that the result has the exponent of the second operand
    result = dec1.quantize(dec2, rounding=rounding)
    assert result.as_tuple().exponent == dec2.as_tuple().exponent

    # Test no InvalidOperation is signaled
    try:
        Decimal(str(dec1)).quantize(Decimal(str(dec2)))
    except decimal.InvalidOperation:
        assert False
# End program