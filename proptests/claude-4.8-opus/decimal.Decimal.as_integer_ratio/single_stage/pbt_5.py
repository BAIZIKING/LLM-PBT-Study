from hypothesis import given, strategies as st
from decimal import Decimal
from fractions import Fraction
from math import gcd

# Summary: Generate Decimals from integers, floats, decimal strings, and special
# values (infinities/NaNs via st.decimals with allow_nan/allow_infinity). For
# special values, assert OverflowError (infinity) or ValueError (NaN). For finite
# values, assert the result is an integer pair (n, d) with d > 0, gcd(n, d) == 1,
# and n/d exactly equals the original Decimal (exact conversion).
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    dec = data.draw(
        st.one_of(
            st.integers().map(Decimal),
            st.floats(allow_nan=False, allow_infinity=False).map(Decimal),
            st.decimals(allow_nan=True, allow_infinity=True),
        )
    )

    if dec.is_nan():
        try:
            dec.as_integer_ratio()
            assert False, "Expected ValueError for NaN"
        except ValueError:
            return

    if dec.is_infinite():
        try:
            dec.as_integer_ratio()
            assert False, "Expected OverflowError for infinity"
        except OverflowError:
            return

    n, d = dec.as_integer_ratio()

    # Return type: pair of integers
    assert isinstance(n, int)
    assert isinstance(d, int)

    # Positive denominator
    assert d > 0

    # Lowest terms
    assert gcd(n, d) == 1

    # Exact conversion
    assert Fraction(n, d) == Fraction(dec)
# End program