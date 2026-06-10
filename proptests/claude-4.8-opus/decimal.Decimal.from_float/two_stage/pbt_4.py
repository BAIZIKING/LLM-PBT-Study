from hypothesis import given, strategies as st
import decimal
import math
from decimal import Decimal

# Property 1: The output is always an instance of Decimal.
@given(
    f=st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(min_value=-10**30, max_value=10**30),
    )
)
def test_decimal_Decimal_from_float_returns_decimal(f):
    result = Decimal.from_float(f)
    assert isinstance(result, Decimal)

# Property 2: For any finite float input, converting the result back to float equals the original input.
@given(
    f=st.floats(allow_nan=False, allow_infinity=False)
)
def test_decimal_Decimal_from_float_roundtrip_float(f):
    result = Decimal.from_float(f)
    assert float(result) == f

# Property 3: For an integer input n, the result equals Decimal(n) exactly with no fractional part.
@given(
    n=st.integers(min_value=-10**30, max_value=10**30)
)
def test_decimal_Decimal_from_float_integer_exact(n):
    result = Decimal.from_float(n)
    assert result == Decimal(n)
    assert result == result.to_integral_value()

# Property 4: Special float values map to their Decimal equivalents.
@given(
    special=st.sampled_from([float('nan'), float('inf'), float('-inf')])
)
def test_decimal_Decimal_from_float_special_values(special):
    result = Decimal.from_float(special)
    if math.isnan(special):
        assert result.is_nan()
    elif special == float('inf'):
        assert result == Decimal('Infinity')
    else:
        assert result == Decimal('-Infinity')

# Property 5: The sign of the output matches the sign of the input.
@given(
    f=st.one_of(
        st.floats(allow_nan=False, allow_infinity=False),
        st.integers(min_value=-10**30, max_value=10**30),
    )
)
def test_decimal_Decimal_from_float_sign(f):
    result = Decimal.from_float(f)
    if f > 0:
        assert result > 0
    elif f < 0:
        assert result < 0
    else:
        assert result == 0
# End program