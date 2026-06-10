from hypothesis import given, strategies as st
from decimal import Decimal, OverflowError, InvalidOperation

@given(st.decimals(allow_nan=True, allow_infinity=True))
def test_as_integer_ratio(value):

    decimal_obj = Decimal(value)

    try:
        n, d = decimal_obj.as_integer_ratio()
        # Asserting the division of n by d is nearly equal (within a small tolerance) to value.
        assert abs(n / d - value) < 1e-10
    except OverflowError:
        # In case of OverflowError, checking if the value was positive or negative infinity.
        assert decimal_obj in (Decimal('Infinity'), Decimal('-Infinity'))
    except InvalidOperation:
        # In case of NaN, verifying the exception raised.
        assert decimal_obj.is_nan()