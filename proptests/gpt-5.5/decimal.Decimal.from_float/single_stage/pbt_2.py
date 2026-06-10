from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Summary: Generate only documented valid inputs: ints and floats.  The strategy
# mixes arbitrary large ints, bools as int instances, arbitrary IEEE-754 64-bit
# floats, and explicit edge-case floats such as NaN, signed infinities, signed
# zero, 0.1, min/max finite floats, and subnormals.  Properties checked:
# Decimal.from_float returns a Decimal; ints/bools are converted exactly;
# finite floats match Decimal(f) exactly; NaN maps to a quiet Decimal NaN; and
# infinities map to signed Decimal infinities.
@given(st.data())
def test_decimal_Decimal_from_float(data):
    int_edges = st.sampled_from([
        0,
        1,
        -1,
        2**53 - 1,
        2**53,
        2**53 + 1,
        -(2**53),
        10**100,
        -(10**100),
    ])
    ints = st.one_of(
        st.booleans(),
        int_edges,
        st.integers(min_value=-(10**200), max_value=10**200),
    )

    float_edges = st.sampled_from([
        0.0,
        -0.0,
        0.1,
        -0.1,
        1.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        5e-324,
        -5e-324,
        2.2250738585072014e-308,
        -2.2250738585072014e-308,
        1.7976931348623157e308,
        -1.7976931348623157e308,
    ])
    floats = st.one_of(
        float_edges,
        st.floats(
            width=64,
            allow_nan=True,
            allow_infinity=True,
            allow_subnormal=True,
        ),
    )

    value = data.draw(st.one_of(ints, floats))
    result = Decimal.from_float(value)

    assert isinstance(result, Decimal)

    if isinstance(value, int):
        assert result == Decimal(int(value))
    elif math.isnan(value):
        assert result.is_qnan()
    elif math.isinf(value):
        expected = Decimal("Infinity") if value > 0 else Decimal("-Infinity")
        assert result == expected
    else:
        assert result == Decimal(value)
        assert float(result) == value

# End program