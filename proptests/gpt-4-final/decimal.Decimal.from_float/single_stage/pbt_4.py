from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.floats(allow_nan=True, allow_infinity=True))
def test_decimal_from_float(f):
    # Convert float to decimal
    result = Decimal.from_float(f)
    
    # Check that the return type is Decimal
    assert isinstance(result, Decimal)
    
    # Check that special float values are correctly converted
    if str(f) == 'nan':
        assert str(result) == 'NaN'
    elif str(f) == 'inf':
        assert str(result) == 'Infinity'
    elif str(f) == '-inf':
        assert str(result) == '-Infinity'
# End program