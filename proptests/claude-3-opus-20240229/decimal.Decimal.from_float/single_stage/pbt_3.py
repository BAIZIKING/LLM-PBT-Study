from hypothesis import given, strategies as st
from decimal import Decimal

# Generate a wide variety of float values including:
# - Finite floats (positive, negative, small, large) 
# - Special values like inf, -inf, and NaN
# - Values very close to 0 
# This exercises different code paths and edge cases.
@given(st.floats(allow_nan=True, allow_infinity=True) | st.just(0.0))
def test_decimal_from_float(f):
    d = Decimal.from_float(f)
    
    # from_float should return a Decimal equal to the input float
    assert d == Decimal(f) 

    # Decimal -> float -> Decimal should give the original Decimal
    assert Decimal.from_float(float(d)) == d

    # Special values should be handled as documented
    if f != f: # NaN
        assert d.is_nan()
    elif f == float('inf'):
        assert d.is_infinite() and d > 0
    elif f == float('-inf'):
        assert d.is_infinite() and d < 0
# End program