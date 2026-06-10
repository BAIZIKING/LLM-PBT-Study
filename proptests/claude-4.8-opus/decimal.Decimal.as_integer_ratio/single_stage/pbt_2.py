from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from math import gcd

# Summary: Generate a wide variety of Decimals — finite values via st.decimals(),
# values built from integers, plus special NaN/Infinity values — then check that
# special values raise the documented exceptions and finite values yield an exact,
# lowest-terms (n, d) pair with a positive denominator.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    finite = st.decimals(allow_nan=False, allow_infinity=False)
    from_int = st.integers().map(Decimal)
    specials = st.sampled_from(['nan', 'snan', 'inf', '-inf', 'Infinity', '-Infinity'])
    special_decimals = specials.map(Decimal)

    value = data.draw(st.one_of(finite, from_int, special_decimals))

    if value.is_nan():
        # NaN inputs must raise ValueError.
        try:
            value.as_integer_ratio()
            assert False, "Expected ValueError for NaN"
        except ValueError:
            pass
    elif value.is_infinite():
        # Infinities must raise OverflowError.
        try:
            value.as_integer_ratio()
            assert False, "Expected OverflowError for infinity"
        except OverflowError:
            pass
    else:
        n, d = value.as_integer_ratio()
        # Returns a pair of ints.
        assert isinstance(n, int)
        assert isinstance(d, int)
        # Denominator must be positive.
        assert d > 0
        # Must be in lowest terms.
        assert gcd(n, d) == 1
        # Conversion must be exact.
        assert Fraction(n, d) == Fraction(value)
# End program