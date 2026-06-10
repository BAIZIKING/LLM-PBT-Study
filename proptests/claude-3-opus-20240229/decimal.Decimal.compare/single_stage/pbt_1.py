from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Summary: 
# Generate a wide variety of Decimal values to compare, including:
# - Small and large values
# - Positive and negative values 
# - Integer-like and fractional values
# - Special values like NaN and infinity
# For each pair of generated values, check the expected properties 
# based on the compare() API documentation.
@given(st.data())
def test_decimal_compare(data):
    a = data.draw(st.one_of(
        st.decimals(allow_nan=True, allow_infinity=True), 
        st.integers(), 
        st.floats(allow_nan=True, allow_infinity=True).map(Decimal)))
    b = data.draw(st.one_of(
        st.decimals(allow_nan=True, allow_infinity=True),
        st.integers(), 
        st.floats(allow_nan=True, allow_infinity=True).map(Decimal)))
    
    context = getcontext()
    result = a.compare(b, context)
    
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    else:
        assert result in [Decimal('-1'), Decimal('0'), Decimal('1')]
        if result == Decimal('-1'):
            assert a < b
        elif result == Decimal('0'):
            assert a == b
        else:
            assert a > b
# End program