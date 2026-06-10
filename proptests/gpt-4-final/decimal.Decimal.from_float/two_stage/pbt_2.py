from hypothesis import given, strategies as st
from decimal import Decimal
import math

@given(st.floats(allow_nan=False, allow_infinity=False, width=32))
def test_output_type_property(f):
    result = Decimal.from_float(f)
    assert isinstance(result, Decimal)

@given(st.floats(allow_nan=False, allow_infinity=False, width=32))
def test_precision_output_property(f):
    accurate_result = Decimal(str(f))
    result = Decimal.from_float(f)
    assert result == accurate_result

@given(st.just(math.nan))
def test_nan_property(f):
    result = Decimal.from_float(f)
    assert math.isnan(result)

@given(st.just(math.inf))
def test_inf_property(f):
    result = Decimal.from_float(f)
    assert result.is_infinite() and result > 0

@given(st.just(-math.inf))
def test_negative_inf_property(f):
    result = Decimal.from_float(f)
    assert result.is_infinite() and result < 0

@given(st.floats(allow_nan=False, allow_infinity=False, width=32))
def test_arithmetic_operations_property(f):
    result = Decimal.from_float(f)
    other = Decimal('1.25')
    try:
        _ = result + other
        _ = result - other
        _ = result * other
        _ = result / other
    except Exception as e:
        assert False, f"Arithmetic operation on decimals failed: {str(e)}"
# End program