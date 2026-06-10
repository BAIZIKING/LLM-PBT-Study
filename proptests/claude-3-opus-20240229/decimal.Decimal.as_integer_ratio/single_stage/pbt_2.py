from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generate a wide range of Decimal values including:
# - Positive and negative numbers 
# - Integers and floats with varying precision
# - Special values like 0, infinity, and NaN
# Test that:
# - Output is a tuple of two integers (numerator, denominator) 
# - The fraction numerator/denominator equals the original Decimal
# - The denominator is always positive
# - Infinities raise OverflowError and NaNs raise InvalidOperation
@given(st.one_of(
    st.decimals(allow_nan=False, allow_infinity=False),
    st.just(Decimal('0')),
    st.just(Decimal('Infinity')), 
    st.just(Decimal('-Infinity')),
    st.just(Decimal('NaN'))
))
def test_decimal_as_integer_ratio(dec):
    try:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert Decimal(n) / Decimal(d) == dec
        assert d > 0
    except OverflowError:
        assert dec in (Decimal('Infinity'), Decimal('-Infinity'))
    except InvalidOperation:  
        assert dec.is_nan()
# End program