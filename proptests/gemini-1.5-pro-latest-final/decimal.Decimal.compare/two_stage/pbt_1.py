@given(a=decimal_strategy(), b=decimal_strategy(), c=decimal_strategy())
def test_compare_transitivity(a, b, c):
    result_ab = decimal.Decimal.compare(a, b)
    result_bc = decimal.Decimal.compare(b, c)
    result_ac = decimal.Decimal.compare(a, c)
    
    if result_ab == decimal.Decimal('1') and result_bc == decimal.Decimal('1'):
        assert result_ac == decimal.Decimal('1')
    elif result_ab == decimal.Decimal('-1') and result_bc == decimal.Decimal('-1'):
        assert result_ac == decimal.Decimal('-1')
    elif result_ab == decimal.Decimal('0') and result_bc == decimal.Decimal('0'):
        assert result_ac == decimal.Decimal('0')
# End program