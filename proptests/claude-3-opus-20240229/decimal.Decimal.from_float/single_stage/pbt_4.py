from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: 
# Generate floating point numbers including:
# - Finite values (both positive and negative) 
# - Special values like inf, -inf, and NaN
# - Values very close to 0
#
# Check the following properties:
# - The result is a Decimal object
# - from_float(float(x)) == Decimal(str(x)) for finite x
# - Decimal.from_float(float('nan')) is a NaN
# - Decimal.from_float(float('inf')) is positive infinity 
# - Decimal.from_float(float('-inf')) is negative infinity

@given(st.one_of(
    st.floats(allow_nan=False, allow_infinity=False),
    st.sampled_from([float('nan'), float('inf'), float('-inf')]),
    st.floats(min_value=-1e-100, max_value=1e-100)
))
def test_decimal_from_float(f):
    d = Decimal.from_float(f)
    assert isinstance(d, Decimal)
    
    if f == float('nan'):
        assert d.is_nan()
    elif f == float('inf'):
        assert d.is_infinite() and d > 0
    elif f == float('-inf'):
        assert d.is_infinite() and d < 0
    else:
        assert d == Decimal(str(f))
# End program        