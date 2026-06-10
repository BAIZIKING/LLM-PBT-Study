from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances with controlled magnitude
def decimal_strategy():
    return st.decimals(
        min_value=-1e10, max_value=1e10, allow_nan=True, allow_infinity=False
    )

@given(a=decimal_strategy(), b=decimal_strategy(), c=decimal_strategy())
def test_decimal_compare_is_decimal(a, b):
    """Output is always a Decimal instance"""
    result = a.compare(b)
    assert isinstance(result, decimal.Decimal)

@given(a=decimal_strategy(), b=decimal_strategy())
def test_decimal_compare_nan(a, b):
    """NaN input leads to NaN output"""
    if a.is_nan() or b.is_nan():
        assert a.compare(b).is_nan()

@given(a=decimal_strategy())
def test_decimal_compare_self(a):
    """Comparison with self is always 0"""
    assert a.compare(a) == decimal.Decimal('0')

@given(a=decimal_strategy(), b=decimal_strategy(), c=decimal_strategy())
def test_decimal_compare_transitive(a, b, c):
    """Comparison is transitive"""
    result_ab = a.compare(b)
    result_bc = b.compare(c)
    result_ac = a.compare(c)
    if result_ab == decimal.Decimal('1') and result_bc == decimal.Decimal('1'):
        assert result_ac == decimal.Decimal('1')
    elif result_ab == decimal.Decimal('-1') and result_bc == decimal.Decimal('-1'):
        assert result_ac == decimal.Decimal('-1')
    elif result_ab == decimal.Decimal('0') and result_bc == decimal.Decimal('0'):
        assert result_ac == decimal.Decimal('0')

@given(a=decimal_strategy(), b=decimal_strategy())
def test_decimal_compare_consistent_arithmetic(a, b):
    """Comparison result is consistent with arithmetic comparison"""
    result = a.compare(b)
    if result == decimal.Decimal('-1'):
        assert a < b
    elif result == decimal.Decimal('0'):
        assert a == b
    elif result == decimal.Decimal('1'):
        assert a > b
# End program