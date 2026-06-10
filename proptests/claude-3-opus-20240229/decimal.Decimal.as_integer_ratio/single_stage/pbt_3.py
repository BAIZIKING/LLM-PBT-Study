from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generate a wide variety of Decimal values, including:
# - Finite positive and negative values with varying scale 
# - Values close to 0 and large magnitude values
# - Special values like NaN and Infinity
# Convert to lowest-terms fraction and check:
# - Numerator/denominator are integers
# - Fraction exactly equals original Decimal value
# - Denominator is always positive
# - Raises expected exceptions for special values
@given(st.one_of(
    st.decimals(allow_nan=False, allow_infinity=False), 
    st.just(Decimal('NaN')),
    st.just(Decimal('Infinity')),
    st.just(Decimal('-Infinity')),
))
def test_decimal_as_integer_ratio(dec):
    try:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert d > 0
        assert Decimal(n) / Decimal(d) == dec
    except OverflowError:
        assert dec in (Decimal('Infinity'), Decimal('-Infinity'))
    except (ValueError, InvalidOperation):
        assert dec.is_nan()
# End program