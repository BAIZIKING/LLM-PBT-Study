from hypothesis import given, strategies as st
from decimal import Decimal
from fractions import Fraction
from math import gcd

# Summary: Generate arbitrary Decimals (finite, NaN, infinity) via st.decimals with
# allow_nan and allow_infinity enabled. For NaN expect ValueError, for infinity expect
# OverflowError, and for finite decimals verify the result is an integer pair with a
# positive denominator, reduced to lowest terms, and exactly equal to the input.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio():
    val = st.data().draw(st.decimals(allow_nan=True, allow_infinity=True))

    if val.is_nan():
        try:
            val.as_integer_ratio()
            assert False, "Expected ValueError for NaN"
        except ValueError:
            pass
    elif val.is_infinite():
        try:
            val.as_integer_ratio()
            assert False, "Expected OverflowError for infinity"
        except OverflowError:
            pass
    else:
        n, d = val.as_integer_ratio()
        assert isinstance(n, int) and isinstance(d, int)
        assert d > 0
        assert gcd(n, d) == 1
        assert Fraction(n, d) == Fraction(val)
# End program