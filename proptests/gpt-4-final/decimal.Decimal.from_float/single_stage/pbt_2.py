from hypothesis import given, strategies as st
from decimal import Decimal

# Generation strategy: Generate random float and integer values, occasionally replace some with 'nan', 'inf', and '-inf'.
# Properties to test: Type of the output is Decimal and special input cases return expected values.
@given(st.one_of(st.floats(allow_nan=False, allow_infinity=False), st.integers()))
def test_decimal_from_float(input):
    # Create edge cases
    if input == 0:
        input = float('nan')
    elif input == 1:
        input = float('inf')
    elif input == -1:
        input = float('-inf')
    # Use Decimal.from_float(...)
    result = Decimal.from_float(input)
    # Check that the type is Decimal
    assert isinstance(result, Decimal)
    # Check special cases
    if str(input) in ['nan', 'inf', '-inf']:
        assert str(result) == str(Decimal(str(input)))
# End program