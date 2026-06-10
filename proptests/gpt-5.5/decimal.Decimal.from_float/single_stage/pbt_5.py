from hypothesis import given, strategies as st
from decimal import Decimal
import math
import pytest

# Summary: Generate valid inputs using ints plus 64-bit floats, with explicit edge cases such as 0.1, infinities, NaN, signed zero, subnormals, and huge integers; also generate invalid non-float/int values to check that they are rejected. For valid inputs, Decimal.from_float must return a Decimal representing the exact float/int value, including NaN and infinities as documented.
@given(st.data())
def test_decimal_Decimal_from_float(data):
    float_edges = st.sampled_from([
        0.1,
        0.0,
        -0.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        5e-324,          # smallest positive subnormal float
        -5e-324,
        1.7976931348623157e308,   # largest finite float
        -1.7976931348623157e308,
    ])

    valid_inputs = st.one_of(
        st.integers(min_value=-(10**100), max_value=10**100),
        st.floats(allow_nan=True, allow_infinity=True, width=64),
        float_edges,
    )

    invalid_inputs = st.one_of(
        st.none(),
        st.text(),
        st.binary(),
        st.lists(st.integers(), max_size=5),
        st.dictionaries(st.text(), st.integers(), max_size=5),
        st.decimals(allow_nan=True, allow_infinity=True),
    )

    f = data.draw(st.one_of(valid_inputs, invalid_inputs))

    if isinstance(f, (float, int)):
        result = Decimal.from_float(f)

        assert isinstance(result, Decimal)

        if isinstance(f, float) and math.isnan(f):
            assert result.is_nan()
        elif isinstance(f, float) and math.isinf(f):
            assert result.is_infinite()
            assert result.is_signed() == (f < 0)
        else:
            assert result.as_integer_ratio() == f.as_integer_ratio()

            if isinstance(f, float):
                assert result == Decimal(f)
            else:
                assert result == Decimal(f)
    else:
        with pytest.raises(TypeError):
            Decimal.from_float(f)

# End program