from hypothesis import given, strategies as st
from decimal import Decimal, OverflowError, InvalidOperation

# Summary: 
# Generate a variety of Decimal inputs, including:
# - Finite numbers (positive, negative, zero)
# - Numbers with different precisions
# - Very large and very small numbers
# - Special values like infinity and NaN
# For each input, check that:
# - The returned tuple (n, d) contains integers
# - n/d equals the original Decimal value
# - The fraction is in lowest terms
# - The denominator is positive
# - OverflowError is raised for infinities
# - InvalidOperation is raised for NaNs
@given(st.one_of(
    st.decimals(allow_nan=False, allow_infinity=False),
    st.decimals(allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100),  
    st.just(Decimal('0')),
    st.just(Decimal('Infinity')),
    st.just(Decimal('-Infinity')),
    st.just(Decimal('NaN'))
))
def test_decimal_as_integer_ratio(dec):
    if dec.is_infinite():
        with pytest.raises(OverflowError):
            dec.as_integer_ratio()
    elif dec.is_nan():
        with pytest.raises(InvalidOperation):
            dec.as_integer_ratio()
    else:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert Decimal(n) / Decimal(d) == dec
        assert d > 0
        g = math.gcd(n, d)
        assert g == 1
# End program