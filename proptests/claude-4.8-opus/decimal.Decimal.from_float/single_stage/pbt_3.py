from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Summary: Generate a wide variety of floats (including nan, inf, -inf, subnormals,
# signed zeros, extreme magnitudes) and integers, since from_float accepts both.
# Check return type is Decimal, correct NaN/Infinity handling, exact float
# round-tripping for finite floats, and exact equality for integers.
@given(st.data())
def test_decimal_Decimal_from_float(data):
    value = data.draw(st.one_of(
        st.floats(),  # includes nan, inf, -inf, subnormals, signed zeros
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e308, max_value=1e308),
        st.integers(),
    ))

    result = Decimal.from_float(value)

    # Property 1: result is always a Decimal
    assert isinstance(result, Decimal)

    if isinstance(value, float):
        if math.isnan(value):
            # Property 2: NaN floats produce NaN Decimals
            assert result.is_nan()
        elif math.isinf(value):
            # Property 3: Infinity preserved with correct sign
            assert result.is_infinite()
            assert (result < 0) == (value < 0)
        else:
            # Property 4: finite floats round-trip exactly back to the float
            assert float(result) == value
            # signed zero: sign should be preserved
            if value == 0.0:
                assert math.copysign(1.0, float(result)) == math.copysign(1.0, value)
    else:
        # Property 5: integer inputs map to an exactly equal Decimal
        assert result == Decimal(value)
        assert result.is_finite()
# End program