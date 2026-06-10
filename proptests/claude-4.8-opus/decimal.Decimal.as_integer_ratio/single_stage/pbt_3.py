from hypothesis import given, strategies as st
from decimal import Decimal, getcontext
from fractions import Fraction
from math import gcd

# Summary: Generate finite Decimals via st.decimals (covering zero, negatives,
# large/small magnitudes, varying precision) plus explicit special values
# (infinities and NaNs). Check error behavior for NaN/Infinity and the
# (n, d) ratio invariants (int types, positive denom, lowest terms, exactness)
# for finite values.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    value = data.draw(
        st.one_of(
            st.decimals(allow_nan=False, allow_infinity=False),
            st.sampled_from([
                Decimal('Infinity'),
                Decimal('-Infinity'),
                Decimal('NaN'),
                Decimal('-NaN'),
                Decimal('sNaN'),
            ]),
        )
    )

    if value.is_nan():
        try:
            value.as_integer_ratio()
            assert False, "Expected ValueError for NaN"
        except ValueError:
            pass
        return

    if value.is_infinite():
        try:
            value.as_integer_ratio()
            assert False, "Expected OverflowError for Infinity"
        except OverflowError:
            pass
        return

    n, d = value.as_integer_ratio()

    # Result is a pair of ints.
    assert isinstance(n, int)
    assert isinstance(d, int)

    # Positive denominator.
    assert d > 0

    # Lowest terms.
    assert gcd(n, d) == 1

    # Conversion is exact: the fraction equals the original Decimal exactly.
    assert Fraction(n, d) == Fraction(value)
# End program