from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: The generation strategy aims to create a diverse range of inputs for testing the from_float method. It includes:
# 1. Normal floats: Randomly generated floats within a wide range.
# 2. Edge cases: Specifically includes NaN, Infinity, -Infinity, and values close to zero.
# 3. Integers: Tests the handling of integer inputs, as the API allows both float and int.
@given(st.data())
def test_decimal_from_float(data):
    # Generate normal floats and edge cases
    float_value = data.draw(st.floats(allow_nan=True, allow_infinity=True))

    # Generate integers to cover int inputs
    int_value = data.draw(st.integers())

    # Test Decimal.from_float for both float and int inputs
    for value in [float_value, int_value]:
        decimal_from_float = Decimal.from_float(value)

        # Property 1: Check if type is Decimal
        assert isinstance(decimal_from_float, Decimal)

        # Property 2: Verify handling of NaN, Infinity, -Infinity
        if math.isnan(value):
            assert math.isnan(decimal_from_float)
        elif math.isinf(value):
            assert math.isinf(decimal_from_float) and decimal_from_float.sign == value.sign
        else:
            # Property 3: For normal floats and integers, compare string representations due to potential precision differences
            assert str(decimal_from_float) == str(Decimal(str(value))) 
# End program 