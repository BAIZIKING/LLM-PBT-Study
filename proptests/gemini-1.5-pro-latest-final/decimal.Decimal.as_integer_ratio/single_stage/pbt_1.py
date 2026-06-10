from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates Decimal instances with varying scales, precisions, signs, and edge cases (inf, -inf, nan)
@given(st.one_of(
    st.decimals(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-float('inf'), max_value=float('inf'), allow_nan=True)
))
def test_decimal_as_integer_ratio(d):
    try:
        n, d = Decimal(d).as_integer_ratio()
        # Check for exact conversion and lowest terms
        assert Decimal(n) / Decimal(d) == Decimal(d)
        assert math.gcd(n, d) == 1
        # Check for positive denominator
        assert d > 0
    except OverflowError:
        # Check for OverflowError on infinities
        assert d in (float('inf'), -float('inf'))
    except ValueError:
        # Check for ValueError on NaNs
        assert math.isnan(d)
# End program