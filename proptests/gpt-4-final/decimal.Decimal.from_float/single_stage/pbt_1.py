from hypothesis import given, strategies as st
from decimal import Decimal

# Generate float values, NaN, infinity, negative infinity, and arbitrary non-float and non-int values
@given(value=st.one_of(st.floats(), st.none(), st.text(), st.bytes(), st.lists(st.integers())))
def test_decimal_from_float(value):
    try:
        res = Decimal.from_float(value)
        
        # For float inputs
        if isinstance(value, float):
            if value == float('inf'):
                assert res == Decimal('Infinity')
            elif value == float('-inf'):
                assert res == Decimal('-Infinity')
            elif str(value) == 'nan':
                assert str(res) == 'NaN'
            else:
                assert res != Decimal(str(value))
        
        # For int inputs
        elif isinstance(value, int):
            assert res == Decimal(str(value))

        # For non-float and non-int inputs
        else:
            assert False, "Decimal.from_float didn't raise TypeError for non-float and non-int inputs"
    except TypeError:
        # It's expected to raise TypeError for non-float and non-int inputs
        if isinstance(value, (float, int)):
            assert False, "Decimal.from_float raised TypeError for float or int inputs"