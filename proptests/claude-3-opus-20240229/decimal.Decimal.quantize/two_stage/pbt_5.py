from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_quantize_exponent_range(x, y):
    context = decimal.getcontext()
    try:
        result = x.quantize(y)
        assert context.Etiny() <= result.as_tuple().exponent <= context.Emax
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        pass
# End program