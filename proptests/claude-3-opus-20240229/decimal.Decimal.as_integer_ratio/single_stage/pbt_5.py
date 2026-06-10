from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Generate a variety of Decimal values including:
# - Small and large magnitudes, both positive and negative 
# - Values with different numbers of significant digits
# - Special values like 0, +/-inf, and NaN
# Use builds() to construct Decimal from float
# Filter to ensure no NaN which would raise ValueError
@given(st.builds(Decimal, 
    st.floats(allow_nan=False, allow_infinity=True)).filter(lambda x: x.is_finite()))
def test_decimal_as_integer_ratio(dec):
    try:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert d > 0
        assert Decimal(n) / Decimal(d) == dec
        assert math.gcd(n, d) == 1
    except InvalidOperation:
        assert dec.is_infinite()
# End program