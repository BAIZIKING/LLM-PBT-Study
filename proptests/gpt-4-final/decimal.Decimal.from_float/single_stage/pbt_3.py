from hypothesis import given, strategies as st, assume
from decimal import Decimal

# Strategy: Generate random integers and floats, and handle special float cases such as 'nan', 'inf' and '-inf'.
@given(st.one_of(st.floats(allow_nan=False, allow_infinity=False), st.integers()))
def test_decimal_from_float(value):
    # We ignore cases where the float is a nan or an infinity.
    assert Decimal.from_float(value) == Decimal(str(value))

@given(st.floats(allow_nan=True, allow_infinity=True))
def test_decimal_from_float_special_cases(value):
    # For nan and infinity, we compare with the corresponding Decimal value.
    if math.isnan(value):
        assert Decimal.from_float(value).is_nan()
    elif math.isinf(value):
        if value > 0:
            assert Decimal.from_float(value) == Decimal('Infinity')
        else:
            assert Decimal.from_float(value) == Decimal('-Infinity')
    else:
        assume(False)
# End program