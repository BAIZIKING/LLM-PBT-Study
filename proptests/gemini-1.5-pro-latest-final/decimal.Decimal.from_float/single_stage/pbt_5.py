from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: This test generates a wide variety of inputs for the Decimal.from_float() method, including normal floats, edge cases like NaN, Infinity, and -Infinity, and values close to the limits of float representation. The properties checked ensure that the resulting Decimal objects have the expected values and that the constructor behaves correctly in different scenarios. 

@given(st.floats(allow_nan=True, allow_infinity=True))
def test_decimal_from_float(f):
    # Create a Decimal object using from_float
    decimal_value = Decimal.from_float(f)

    # Check for expected values and behaviors
    if f == float('inf'):
        assert decimal_value == Decimal('Infinity')
    elif f == float('-inf'):
        assert decimal_value == Decimal('-Infinity')
    elif f != f:  # Check for NaN
        assert decimal_value.is_nan()
    else:
        # Compare the string representations of the Decimal and float for approximate equality
        assert str(decimal_value) == str(Decimal(str(f)))
# End program