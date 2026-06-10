from hypothesis import given, strategies as st
import decimal
from decimal import Decimal, InvalidOperation

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_exponent(val1, val2):
    result = val1.quantize(val2)
    assert result.as_tuple().exponent == val2.as_tuple().exponent

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_precision(val1, val2):
    context = decimal.getcontext()
    try:
        result = val1.quantize(val2)
        assert len(result.as_tuple().digits) <= context.prec
    except InvalidOperation:
        assert len(val1.as_tuple().digits) > context.prec

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_no_underflow(val1, val2):
    decimal.getcontext().traps[decimal.Underflow] = True
    try:
        val1.quantize(val2)
    except decimal.Underflow:
        assert False

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.sampled_from([None, decimal.ROUND_UP, decimal.ROUND_DOWN, decimal.ROUND_CEILING, decimal.ROUND_FLOOR, decimal.ROUND_HALF_UP, decimal.ROUND_HALF_DOWN, decimal.ROUND_HALF_EVEN]))
def test_decimal_quantize_rounding(val1, val2, rounding):
    if val2.as_tuple().exponent > val1.as_tuple().exponent:
        result = val1.quantize(val2, rounding=rounding)
        assert result == val1.quantize(val2, rounding=rounding or decimal.getcontext().rounding)
    else:
        result = val1.quantize(val2)
        assert result == val1

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False).filter(lambda x: x.adjusted() > decimal.getcontext().Emax or x.adjusted() < decimal.getcontext().Etiny()))
def test_decimal_quantize_exponent_bounds(val1, val2):
    try:
        val1.quantize(val2)
        assert False
    except decimal.InvalidOperation:
        pass
# End program