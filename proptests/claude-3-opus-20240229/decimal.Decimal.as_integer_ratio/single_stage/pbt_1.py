from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation, DivisionByZero

# Summary: 
# Generate a wide variety of decimal values including:
# - Finite decimals with varying digit counts, before and after decimal point
# - Decimals with trailing zeros and exact values
# - Minimum and maximum decimals supported by the implementation
# - Special values like 0, +Inf, -Inf, NaN
# For the generated decimal d, check that:
# - as_integer_ratio() returns a tuple (n, d) containing integers
# - n/d equals the original decimal value
# - d is always positive
# - n and d are in lowest terms (gcd is 1) 
# - OverflowError is raised for infinities
# - InvalidOperation is raised for NaNs
@given(st.decimals(allow_nan=True, allow_infinity=True) | st.just(Decimal('0')))
def test_decimal_as_integer_ratio(dec):
    try:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert Decimal(n) / Decimal(d) == dec
        assert d > 0
        assert math.gcd(n, d) == 1
    except OverflowError:
        assert dec in (Decimal('Inf'), Decimal('-Inf')) 
    except InvalidOperation:  
        assert dec.is_nan()
# End program