from hypothesis import given, strategies as st
from decimal import Decimal

# Generation strategy:
# We're generating two sets of decimal numbers, including infinities and NaNs. 
@given(st.floats(allow_infinity=True, allow_nan=True), st.floats(allow_infinity=True, allow_nan=True))
def test_decimal_compare(a, b):
    result = Decimal(a).compare(Decimal(b))
    # Checking if correct value is returned, based on the comparison
    if a is None or b is None or a != a or b != b: # if any value is NaN
        assert result != result # result should be NaN
    elif a < b:
        assert result == Decimal('-1')
    elif a == b:
        assert result == Decimal('0')
    elif a > b:
        assert result == Decimal('1')
    else:
        assert False # This shouldn't occur