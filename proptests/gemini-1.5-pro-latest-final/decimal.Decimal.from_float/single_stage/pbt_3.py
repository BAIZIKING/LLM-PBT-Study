from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate floats, special values (NaN, infinities), and integers.
@given(st.one_of(
    st.floats(allow_nan=False, allow_infinity=False),  # Normal floats
    st.just(float('nan')),  # NaN
    st.just(float('inf')),  # Positive infinity
    st.just(float('-inf')),  # Negative infinity
    st.integers()  # Integers
))
def test_decimal_from_float(f):
    decimal_value = Decimal.from_float(f)
    
    if f in (float('nan'), float('inf'), float('-inf')):
        # Check for correct handling of special values
        assert str(decimal_value) == str(Decimal(str(f)))
    else:
        # Check for correct conversion of normal floats and integers
        assert str(decimal_value) == str(Decimal(f"{f:.50f}"))  # Compare up to 50 decimal places

# End program