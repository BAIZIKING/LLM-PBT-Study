from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Set a longer precision
getcontext().prec = 50

@given(st.decimals(), st.decimals(), st.decimals())
def test_fma_property(decimal_a, decimal_b, decimal_c):
    result = decimal_a.fma(decimal_b, decimal_c)

    # Test 1: Output is always a Decimal
    assert isinstance(result, Decimal)

    # Test 2: Order of operations are followed
    assert result == (decimal_a * decimal_b + decimal_c)

    # Test 3: Direct correspondence to arithmetic result
    temp_result = (decimal_a * decimal_b) + decimal_c
    assert result == temp_result

    # Test 4: Handles edge cases correctly
    if decimal_c == 0:
        assert result == (decimal_a * decimal_b)

    # Test  5: Should not result in any rounding
    temp_result = (decimal_a * decimal_b)
    # Use almost equal to allow for acceptable floating point error
    assert temp_result.quantize(Decimal('.00000')) == (result - decimal_c).quantize(Decimal('.00000'))

# End program