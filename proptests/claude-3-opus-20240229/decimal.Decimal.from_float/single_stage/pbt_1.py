from hypothesis import given, strategies as st
from decimal import Decimal

# Generate a wide variety of float values, including:
# - Finite floats (both positive and negative) 
# - Floats close to 0
# - Very large and very small floats
# - Inf, -Inf, and NaN
# This checks a range of normal cases and edge cases.
@given(st.floats(allow_nan=True, allow_infinity=True) | st.just(0.0))
def test_decimal_from_float(f):
    d = Decimal.from_float(f)
    
    # from_float should return a Decimal equivalent to the float
    assert d == Decimal(f) 
    
    # Check some properties based on math with inf, -inf, nan
    if math.isinf(f):
        assert d.is_infinite()
        assert math.copysign(1, f) == d.copy_sign(1).number_class()
    elif math.isnan(f):
        assert d.is_nan()
    else:
        assert d.is_finite()
        
    # Decimal value should be closer to f than adjacent floats
    assert abs(d - Decimal(f)) <= abs(Decimal(math.nextafter(f, 0)) - d)
    assert abs(d - Decimal(f)) <= abs(Decimal(math.nextafter(f, math.inf)) - d)
# End program