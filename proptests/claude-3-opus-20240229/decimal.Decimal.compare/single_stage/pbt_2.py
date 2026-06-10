from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate a wide variety of Decimal values, including:
# - Finite values with varying precisions, signs, and magnitudes 
# - Special values like NaN, sNaN, -Infinity, Infinity, and -0/+0
# Compare the generated values to check properties based on the docs.
@given(st.data())
def test_decimal_compare(data):
    # Generate finite decimals with varying precisions, signs, magnitudes
    finite_val = data.draw(st.decimals(allow_nan=False, allow_infinity=False))
    
    # Generate special decimal values 
    special_vals = [Decimal('NaN'), Decimal('sNaN'), Decimal('-Infinity'), 
                    Decimal('Infinity'), Decimal('-0'), Decimal('+0')]
    special_val = data.draw(st.sampled_from(special_vals))
    
    # Compare decimals and check properties
    result = finite_val.compare(special_val)
    
    if finite_val == special_val:
        assert result == Decimal('0') # a == b ==> Decimal('0')
    elif special_val.is_nan():  
        assert result.is_nan()  # a or b is a NaN ==> Decimal('NaN')
    elif finite_val < special_val:
        assert result == Decimal('-1') # a < b ==> Decimal('-1') 
    elif finite_val > special_val:
        assert result == Decimal('1') # a > b ==> Decimal('1')
# End program