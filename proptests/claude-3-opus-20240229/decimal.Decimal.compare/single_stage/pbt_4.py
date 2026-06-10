from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Summary: 
# Generate a wide variety of Decimal values, including:
# - Finite values with random precision, exponent, and sign
# - Special values like NaN, sNaN, +/-Infinity, +/-0
# Compare the generated values and check properties based on the API docs
@given(st.data())
def test_decimal_compare(data):
    # Generate random precision and context
    prec = data.draw(st.integers(min_value=1, max_value=100))
    getcontext().prec = prec
    
    # Generate pairs of random Decimal values
    a = data.draw(st.one_of(
        st.decimals(allow_nan=True, allow_infinity=True), 
        st.sampled_from([Decimal('0'), Decimal('-0')])
    ))
    b = data.draw(st.one_of(
        st.decimals(allow_nan=True, allow_infinity=True),
        st.sampled_from([Decimal('0'), Decimal('-0')])
    ))
    
    # Compare the values and check properties
    result = a.compare(b)
    
    # If either value is NaN, result should be NaN
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    # Check cases for less than, equal, greater than
    elif a < b:
        assert result == Decimal('-1') 
    elif a == b:
        assert result == Decimal('0')
    elif a > b:
        assert result == Decimal('1')
# End program