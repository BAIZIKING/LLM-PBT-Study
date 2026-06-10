from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: 
# Generate floats using various strategies:
# - finite floats between -1e100 and 1e100 
# - special values like inf, -inf, and NaN
# - floats very close to 0
# Check that:
# - from_float returns a Decimal 
# - result equals Decimal(str(f)) for finite floats
# - inf, -inf and NaN map to proper Decimal values
@given(st.one_of(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100),
    st.sampled_from([float('inf'), float('-inf'), float('nan')]),
    st.floats(min_value=-1e-100, max_value=1e-100)
))
def test_decimal_from_float(f):
    d = Decimal.from_float(f)
    assert isinstance(d, Decimal)
    if f == float('inf'):
        assert d == Decimal('Infinity')
    elif f == float('-inf'):
        assert d == Decimal('-Infinity')  
    elif f != f: # only NaN doesn't equal itself
        assert d.is_nan()
    else:
        assert d == Decimal(str(f))
# End program