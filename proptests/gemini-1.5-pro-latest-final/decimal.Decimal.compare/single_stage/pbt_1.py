from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates random Decimal numbers and NaN, and checks the compare function's output against expected results.
@given(st.data())
def test_decimal_compare(data):
    # Generate random Decimal numbers and NaNs
    num1 = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    num2 = data.draw(st.decimals(allow_nan=True, allow_infinity=True))

    # Perform comparison
    result = Decimal.compare(num1, num2)

    # Check properties based on inputs and expected outcomes
    if num1 != num1 or num2 != num2:  # Check for NaN
        assert result != result  # Assert result is also NaN
    elif num1 < num2:
        assert result == Decimal('-1')
    elif num1 == num2:
        assert result == Decimal('0')
    else:
        assert result == Decimal('1')
# End program