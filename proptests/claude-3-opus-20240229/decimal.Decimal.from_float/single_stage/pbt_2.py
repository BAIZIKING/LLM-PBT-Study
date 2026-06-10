from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Summary: Generate floats using various strategies:
# - finite floats (both positive and negative) 
# - inf/-inf/nan
# - floats very close to 0
# Then check that the resulting Decimal matches the documentation:
# - from_float(f) should exactly match Decimal(str(f)) 
# - from_float(nan/inf/-inf) should result in Decimal nan/inf/-inf
@given(st.one_of(
    st.floats(allow_nan=False, allow_infinity=False),
    st.sampled_from([float('nan'), float('inf'), float('-inf')]),
    st.floats(min_value=-1e-100, max_value=1e-100)
))
def test_decimal_from_float(f):
    d = Decimal.from_float(f)
    
    if math.isnan(f):
        assert d.is_nan()
    elif math.isinf(f):
        assert d.is_infinite()
        assert d.is_signed() == (f < 0)
    else:
        assert d == Decimal(str(f))
# End program        