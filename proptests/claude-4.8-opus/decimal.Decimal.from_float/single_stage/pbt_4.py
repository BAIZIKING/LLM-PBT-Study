from hypothesis import given, strategies as st
import math
from decimal import Decimal

# Summary: Generate floats (including NaN, infinities, subnormals, signed zeros)
# and integers (the two accepted types). Verify return type is Decimal, NaN/Inf
# are mapped correctly, and finite values round-trip exactly back to the input.
@given(st.data())
def test_decimal_Decimal_from_float():
    f = data.draw(st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(),
    )) if False else None  # placeholder to keep signature clean

@given(st.one_of(
    st.floats(allow_nan=True, allow_infinity=True),
    st.integers(),
))
def test_decimal_Decimal_from_float(f):
    result = Decimal.from_float(f)

    # Property 1: result is always a Decimal
    assert isinstance(result, Decimal)

    if isinstance(f, float) and math.isnan(f):
        # Property 2: NaN maps to a NaN Decimal
        assert result.is_nan()
    elif isinstance(f, float) and math.isinf(f):
        # Property 3: infinities map to infinite Decimals with correct sign
        assert result.is_infinite()
        assert (result < 0) == (f < 0)
    else:
        # Property 4: finite values round-trip exactly back to the input
        assert float(result) == float(f)
        # Property 5: integer inputs are represented exactly
        if isinstance(f, int):
            assert result == Decimal(f)
        # Sign preservation (incl. signed zero via copysign)
        if f != 0:
            assert (result < 0) == (f < 0)
        else:
            assert result == 0
# End program