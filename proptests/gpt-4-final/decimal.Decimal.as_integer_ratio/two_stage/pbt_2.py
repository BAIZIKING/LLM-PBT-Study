from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_type(result):
    ratio = result.as_integer_ratio()
    assert isinstance(ratio, tuple) and len(ratio) == 2, "Should return a tuple of length 2"

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_integer_output(result):
    n, d = result.as_integer_ratio()
    assert isinstance(n, int) and isinstance(d, int), "Both elements should be integers"

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_exact_conversion(result):
    n, d = result.as_integer_ratio()
    assert decimal.Decimal(n) / decimal.Decimal(d) == result, "The ratio should be equal to the original Decimal"

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_negative_numbers(result):
    n, d = result.as_integer_ratio()
    assert (n < 0 and d > 0 and result < 0) or (n >= 0 and d > 0 and result >= 0), "Signs should be correct"

@given(st.just(decimal.Decimal('Infinity')))
def test_decimal_as_integer_ratio_overflow_error(result):
    with pytest.raises(OverflowError):
        result.as_integer_ratio()

@given(st.just(decimal.Decimal('NaN')))
def test_decimal_as_integer_ratio_value_error(result):
    with pytest.raises(ValueError):
        result.as_integer_ratio()
# End program