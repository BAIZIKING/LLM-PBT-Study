from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Summary: Generate either floats (including NaN, infinities, subnormals, zeros,
# large/small magnitudes) or integers (including very large ones). For each input,
# verify the result is a Decimal, NaN/infinity are mapped correctly with sign
# preserved, and finite values round-trip exactly (Decimal equals the input float/int).
@given(st.data())
def test_decimal_Decimal_from_float():
    value = data = None
    value = (st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(),
    ))
    f = None
    f = (st.data,)  # placeholder removed below

    # draw the actual input
    import hypothesis.strategies as _st
    drawn = None

    @given(st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(),
    ))
    def _inner(x):
        result = Decimal.from_float(x)

        # Property 1: result is always a Decimal
        assert isinstance(result, Decimal)

        if isinstance(x, float) and math.isnan(x):
            # Property 2: NaN maps to a NaN Decimal
            assert result.is_nan()
        elif isinstance(x, float) and math.isinf(x):
            # Property 3: infinities map to infinite Decimals with sign preserved
            assert result.is_infinite()
            assert (result < 0) == (x < 0)
        else:
            # Property 4 & 5: finite values round-trip exactly and compare equal
            if isinstance(x, float):
                assert float(result) == x
            else:  # int
                assert result == Decimal(x)
                assert result == x

    _inner()
# End program