@given(a=decimal_strategy(), b=decimal_strategy(), c=decimal_strategy())
def test_compare_transitivity(a, b, c):
    result_ab = a.compare(b)
    result_bc = b.compare(c)
    result_ac = a.compare(c)
    # Transitivity cases for <, >, and == comparisons
    if result_ab == decimal.Decimal('-1') and result_bc == decimal.Decimal('-1'):
        assert result_ac == decimal.Decimal('-1')
    elif result_ab == decimal.Decimal('1') and result_bc == decimal.Decimal('1'):
        assert result_ac == decimal.Decimal('1')
    elif result_ab == decimal.Decimal('0') and result_bc == decimal.Decimal('0'):
        assert result_ac == decimal.Decimal('0')
# End program