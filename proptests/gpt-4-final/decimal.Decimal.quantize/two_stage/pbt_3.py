from hypothesis import given, strategies as st
import decimal
from decimal import Decimal, InvalidOperation 

@given(st.decimals(min_value=-999, max_value=999, allow_nan=False, allow_infinity=False, places=6),
       st.decimals(min_value=-999, max_value=999, allow_nan=False, allow_infinity=False, places=2),
       st.sampled_from([None]+[getattr(decimal, attr) for attr in dir(decimal) if attr.startswith('ROUND_')]))
def test_decimal_quantize_property(decimal1, decimal2, rounding):
    try:
        result = decimal1.quantize(decimal2, rounding)

        assert isinstance(result, Decimal)
        assert result <= decimal1
        assert len(str(result).partition('.')[2]) <= len(str(decimal2).partition('.')[2])

        if len(str(result).partition('.')[2]) > len(str(decimal1).partition('.')[2]):
            assert "InvalidOperation" in str(e)

        exponent_result = int(str(result).partition('E')[2] if 'E' in str(result) else 0)
        assert exponent_result >= Decimal.getcontext().Emin
        assert exponent_result <= Decimal.getcontext().Emax

    except decimal.InvalidOperation as e:

        if "quantize result has too many digits for current context" in str(e):
            assert "InvalidOperation" in str(e)

# End program