from hypothesis import given, strategies as st
from decimal import Decimal

# We use strategies to generate a wide range of input including small and large decimal numbers.
# We check the Decimal.fma function by manually verifying results and also checking for Decimal object return type. 

@given(st.floats(min_value=-1e20, max_value=1e20), st.floats(min_value=-1e20, max_value=1e20), st.floats(min_value=-1e20, max_value=1e20))
def test_decimal_fma(a, b, c):
    # Convert floats to Decimal to work with decimal package
    a = Decimal(str(a))
    b = Decimal(str(b))
    c = Decimal(str(c))
    
    # Call our function under test
    result = a.fma(b, c)
    
    # Check our result is a Decimal instance
    assert isinstance(result, Decimal)
    
    # Check operation correctness
    expected_result = a*b + c
    assert result == expected_result
# End program