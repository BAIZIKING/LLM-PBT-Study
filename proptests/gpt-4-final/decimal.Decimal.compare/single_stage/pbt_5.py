from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.tuples(st.floats(allow_infinity=False, allow_nan=True),
                 st.floats(allow_infinity=False, allow_nan=True)))
def test_decimal_compare(t):
    a, b = t
    result = Decimal(a).compare(Decimal(b))
    # Checking properties
    if Decimal(a).is_nan() or Decimal(b).is_nan():
        assert result.is_nan(), "Expected NaN"
    elif a < b:
        assert result == Decimal('-1'), "Expected -1"
    elif a == b:
        assert result == Decimal('0'), "Expected 0"
    elif a > b:
        assert result == Decimal('1'), "Expected 1"
# End program