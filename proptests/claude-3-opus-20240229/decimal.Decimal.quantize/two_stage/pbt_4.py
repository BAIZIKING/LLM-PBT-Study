from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_exponent_equality(d1, d2):
    result = d1.quantize(d2)
    assert result.as_tuple().exponent == d2.as_tuple().exponent
    
@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_invalid_operation(d1, d2):
    context = decimal.getcontext()
    precision = context.prec
    try:
        result = d1.quantize(d2)
        assert len(str(result.quantize(decimal.Decimal(1)) - result)) <= precision
    except decimal.InvalidOperation:
        assert True
        
@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_no_underflow(d1, d2):
    context = decimal.getcontext()
    etiny = context.Etiny()
    try:
        result = d1.quantize(d2)
        assert result.adjusted() >= etiny
    except decimal.InvalidOperation:
        assert True
        
@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.sampled_from([None, decimal.ROUND_DOWN, decimal.ROUND_HALF_UP, decimal.ROUND_HALF_EVEN, decimal.ROUND_CEILING, decimal.ROUND_FLOOR, decimal.ROUND_UP, decimal.ROUND_05UP]))
def test_decimal_quantize_rounding(d1, d2, rounding):
    if d2.adjusted() < d1.adjusted():
        try:
            result = d1.quantize(d2, rounding=rounding)
            assert result == d1.quantize(d2, rounding=rounding)
        except decimal.InvalidOperation:
            assert True
            
@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_exponent_range(d1, d2):
    context = decimal.getcontext()
    emax = context.Emax
    etiny = context.Etiny()
    try:
        result = d1.quantize(d2)
        assert etiny <= result.adjusted() <= emax
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        assert True
# End program