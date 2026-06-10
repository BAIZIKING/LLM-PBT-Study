from hypothesis import given, example, strategies as st
from decimal import Decimal, getcontext, InvalidOperation
import math

@given(st.decimals(allow_infinity=False, allow_nan=False).filter(lambda x: x.is_finite()), st.integers(-10, 10))
def test_decimal_quantize(d: Decimal, exp: int):
    context = getcontext()

    # Determine the limit of precision
    max_coef_length = context.prec

    # Adjust coefficient length
    q = Decimal((0, (int('1' * max_coef_length),), exp))

    try:
        result = d.quantize(q)
    except InvalidOperation:
        # Check if the coefficient length > precision after quantize
        assert abs(math.log10(abs(d))) + abs(exp) > max_coef_length
    else:
        # Check if the result has the same exponent as the quantize value
        assert result.as_tuple().exponent == q.as_tuple().exponent

        # Check if the result is not underflowed
        assert context.flags["Underflow"] == False
    
        # Check if the rounding occured based on context
        assert result == round(d, -exp)
        
        # check that it does not return a value if the resulting exponent is > Emax or < Etiny()
        assert not (result.as_tuple().exponent > context.Emax or result.as_tuple().exponent < context.Etiny())

# End program