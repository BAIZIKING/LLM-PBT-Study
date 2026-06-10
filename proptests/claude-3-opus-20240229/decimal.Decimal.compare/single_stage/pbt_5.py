from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate a wide variety of Decimal values, including:
# - Finite numbers (positive, negative, zero) 
# - Special values (NaN, -Inf, +Inf)
# - Numbers with different precisions
# Then compare pairs of generated values to check the expected 
# return values according to the API docs.
@given(st.data())
def test_decimal_compare(data):
    # Generate finite numbers, special values, and precisions
    finite_val = st.floats(allow_nan=False, allow_infinity=False)
    special_val = st.sampled_from([Decimal('NaN'), Decimal('-Inf'), Decimal('Inf')])
    precision = st.integers(min_value=1, max_value=100)
    
    # Draw random Decimal values with different properties
    a = data.draw(st.one_of(
        st.builds(Decimal, finite_val), 
        special_val,
        st.builds(Decimal, finite_val, precision)))
    b = data.draw(st.one_of(
        st.builds(Decimal, finite_val),
        special_val, 
        st.builds(Decimal, finite_val, precision)))
    
    # Compare values and check return value
    c = a.compare(b)
    if a.is_nan() or b.is_nan():
        assert c.is_nan()
    elif a < b:
        assert c == Decimal('-1') 
    elif a == b:
        assert c == Decimal('0')
    elif a > b:
        assert c == Decimal('1')
# End program