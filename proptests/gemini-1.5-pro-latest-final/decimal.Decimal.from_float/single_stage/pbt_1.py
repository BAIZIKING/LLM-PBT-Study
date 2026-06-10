from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates normal floats, special values (NaN, infinities), and edge cases.
@given(st.floats(allow_nan=True, allow_infinity=True))
def test_decimal_from_float(f):
    try:
        decimal_value = Decimal.from_float(f)
        
        # Check conversion accuracy for normal floats
        if not math.isnan(f) and not math.isinf(f):
            assert abs(decimal_value - Decimal(str(f))) < Decimal("1e-15")

        # Check special value handling
        if math.isnan(f):
            assert decimal_value.is_nan()
        elif math.isinf(f):
            assert decimal_value.is_infinite() and decimal_value.is_signed() == (f < 0)
        elif f == 0:
            assert decimal_value == Decimal("0")
    except TypeError:
        # Check error handling for non-float inputs
        assert not isinstance(f, (float, int))

# End program