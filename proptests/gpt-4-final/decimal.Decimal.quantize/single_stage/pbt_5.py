from hypothesis import given, strategies as st
from decimal import Decimal, DecimalException, getcontext, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_UP, ROUND_DOWN, ROUND_FLOOR, ROUND_CEILING, Context

rounding_strategies = [ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_UP, ROUND_DOWN, ROUND_FLOOR, ROUND_CEILING]

@given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False), 
       st.sampled_from(rounding_strategies), st.integers(min_value=1, max_value=28))
def test_decimal_quantize(decimal1, decimal2, rounding, precision):
    decimal1 = Decimal(str(decimal1))
    decimal2 = Decimal(str(decimal2))
    context = Context(prec=precision, rounding=rounding)

    try:
        result = decimal1.quantize(decimal2, rounding, context)
    except DecimalException:
        pass # Catching expected exceptions because under some circumstances the operation could be invalid
    else:
        assert result == decimal1.quantize(decimal2, rounding, context)
        assert result.exp <= context.Emax
        assert result.exp >= context.Etiny()