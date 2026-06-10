from hypothesis import given, strategies as st
from decimal import Decimal, OverflowError, ValueError

# Summary: Generates a wide range of Decimal values including edge cases
@given(st.one_of(
    st.decimals(min_value=-1e100, max_value=1e100, allow_infinity=True, allow_nan=True),
    st.decimals(
        min_value=-1, 
        max_value=1, 
        allow_infinity=False, 
        allow_nan=False
    ).map(lambda x: Decimal(str(x)) # Generate repeating decimals
)))
def test_decimal_as_integer_ratio(dec):
    if dec in (Decimal('inf'), Decimal('-inf')):
        with pytest.raises(OverflowError):
            dec.as_integer_ratio()
    elif dec.is_nan():
        with pytest.raises(ValueError):
            dec.as_integer_ratio()
    else:
        n, d = dec.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert d > 0
        assert n == dec * d
        # Check if the fraction is in lowest terms
        assert math.gcd(n, d) == 1 
# End program