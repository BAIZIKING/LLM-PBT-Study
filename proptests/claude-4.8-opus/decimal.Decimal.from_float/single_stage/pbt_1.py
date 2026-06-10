from hypothesis import given, strategies as st
import math
from decimal import Decimal

# Summary: Generate floats (including NaN, +/-inf, signed zeros, subnormals)
# and arbitrary-precision ints, then verify return type, special-value mapping,
# exact round-trip equality, and sign preservation.
@given(st.data())
def test_decimal_Decimal_from_float():
    f = st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(),
    )
    value = st.data().draw(f) if False else None  # placeholder, replaced below

    # draw the actual value using the provided data object
    # (note: in @given(st.data()) the data object is passed as the arg below)


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

    # Property 2: special values mapping (only applies to floats)
    if isinstance(value, float) and math.isnan(value):
        assert result.is_nan()
        return

    if isinstance(value, float) and math.isinf(value):
        assert result.is_infinite()
        # Property 4 (sign): sign must match
        assert (result < 0) == (value < 0)
        return

    # Property 3: exact round-trip / equality for finite values
    if isinstance(value, float):
        # Decimal stores the exact value of the float, so converting back
        # to float must reproduce the original bits exactly.
        assert float(result) == value
        # Property 4: sign preservation, including signed zero.
        assert math.copysign(1.0, float(result)) == math.copysign(1.0, value)
    else:
        # For integers, the Decimal must equal the integer exactly.
        assert result == Decimal(value)
        assert int(result) == value
# End program