from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Summary: Generate a wide variety of Decimal values, including:
# - Finite numbers with varying precision and exponent
# - Special values like NaN, sNaN, -Infinity, Infinity, and 0
# - Values near important boundaries (0, 1, -1, min/max)
# Compare the generated values to each other and check that:  
# - Comparing a value to itself returns 0
# - Comparing a value to NaN returns NaN  
# - x < y iff compare(x, y) == -1
# - x > y iff compare(x, y) == 1
# - x == y iff compare(x, y) == 0
@given(st.data())
def test_decimal_compare(data):
    # Generate a variety of Decimal values
    decimals = st.one_of(
        st.decimals(allow_nan=True, allow_infinity=True),
        st.sampled_from([Decimal('0'), Decimal('-0'), 
                         Decimal('1'), Decimal('-1'), 
                         Decimal('1e999'), Decimal('-1e999')])
    )
    
    x, y = data.draw(st.tuples(decimals, decimals))
    cmp = Decimal.compare(x, y)
    
    # Check key properties
    assert Decimal.compare(x, x) == 0
    if x.is_nan() or y.is_nan():
        assert cmp.is_nan()
    else:
        assert (x < y) == (cmp == -1)
        assert (x > y) == (cmp == 1) 
        assert (x == y) == (cmp == 0)
# End program