from hypothesis import given, strategies as st
from decimal import Decimal
from math import gcd

# Summary: Generate decimals including NaN and infinities (to verify the
# documented OverflowError/ValueError behavior) as well as a wide range of
# finite decimals (varying sign, magnitude, and precision). For finite inputs,
# verify the result is a pair of ints, the denominator is positive, the fraction
# is in lowest terms (gcd == 1), and that n/d exactly reconstructs the input.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    d = data.draw(st.decimals(allow_nan=True, allow_infinity=True))

    if d.is_nan():
        try:
            d.as_integer_ratio()
            assert False, "Expected ValueError on NaN"
        except ValueError:
            pass
    elif d.is_infinite():
        try:
            d.as_integer_ratio()
            assert False, "Expected OverflowError on infinity"
        except OverflowError:
            pass
    else:
        n, denom = d.as_integer_ratio()
        assert isinstance(n, int)
        assert isinstance(denom, int)
        assert denom > 0
        assert gcd(n, denom) == 1
        # Exact conversion: d == n / denom  <=>  d * denom == n (exactly).
        assert Decimal(n) == d * denom
# End program