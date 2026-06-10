from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Summary: Generate floats (including NaN, +/-inf, subnormals, signed zeros)
# and arbitrary integers, since from_float accepts both float and int.
# Verify the result is always a Decimal, that special float values map to
# NaN/Infinity correctly, that finite values are stored exactly (round-trip),
# and that from_float agrees with the direct Decimal constructor.
@given(st.data())
def test_decimal_Decimal_from_float(data):
    value = data.draw(
        st.one_of(
            st.floats(allow_nan=True, allow_infinity=True),
            st.integers(),
        )
    )

    result = Decimal.from_float(value)

    # Property 1: result is always a Decimal
    assert isinstance(result, Decimal)

    if isinstance(value, float):
        if math.isnan(value):
            # Property 2a: NaN float -> NaN Decimal
            assert result.is_nan()
        elif math.isinf(value):
            # Property 2b/2c: infinities map correctly with matching sign
            assert result.is_infinite()
            assert (result > 0) == (value > 0)
        else:
            # Property 3: finite floats are stored exactly (round-trips back)
            assert float(result) == value
            # Property 4: agrees with direct constructor (Python >= 3.2)
            assert result == Decimal(value)
    else:
        # int input: exact integer value is preserved
        assert result == Decimal(value)
        assert int(result) == value
# End program