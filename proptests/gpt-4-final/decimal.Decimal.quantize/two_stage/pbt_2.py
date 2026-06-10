from hypothesis import given, strategies as st
from decimal import Decimal, Context, InvalidOperation

@given(st.decimals(), st.decimals(allow_nan=False, allow_infinity=False), 
       st.sampled_from([None] + list(Context.rounding)), st.none() | st.builds(Context))
def test_quantize_property(d1, d2, rounding, context):
    maxexp = 999999999
    minexp = -999999999
    d1 = d1.quantize(Decimal('1.00000000'))
    d2 = d2.quantize(Decimal('1.00000000')) if abs(d2) <= maxexp else maxexp

    try:
        result = d1.quantize(d2, rounding=rounding, context=context)
    except InvalidOperation:
        assert len(str(abs(d1))) > (context or Context()).prec
        return

    if abs(d2) > maxexp or abs(d2) < minexp:
        assert isinstance(result, InvalidOperation)
    else:
        assert isinstance(result, Decimal)
        assert result.as_tuple().exponent == d2.as_tuple().exponent
# End program