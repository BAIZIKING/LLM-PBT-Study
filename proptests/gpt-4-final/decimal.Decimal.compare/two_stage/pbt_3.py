from hypothesis import given, strategies as st
import decimal

@given(st.decimals(), st.decimals())
def test_compare_same_numbers(decimal1, decimal2):
    assert decimal1.compare(decimal1) == decimal.Decimal(0)
    assert decimal2.compare(decimal2) == decimal.Decimal(0)

@given(st.tuples(st.decimals(), st.decimals()).filter(lambda x: x[0] < x[1]))
def test_compare_smaller_to_larger(pair):
    assert pair[0].compare(pair[1]) == decimal.Decimal(-1)

@given(st.tuples(st.decimals(), st.decimals()).filter(lambda x: x[0] > x[1]))
def test_compare_larger_to_smaller(pair):
    assert pair[0].compare(pair[1]) == decimal.Decimal(1)

@given(st.decimals(), st.just(decimal.Decimal('NaN')))
def test_compare_with_NaN(decimal1, _):
    assert decimal1.compare(decimal.Decimal('NaN')) == decimal.Decimal('NaN')

@given(st.decimals(), st.decimals())
def test_compare_result_values(decimal1, decimal2):
    result = decimal1.compare(decimal2)
    assert result in {decimal.Decimal('NaN'), decimal.Decimal('0'), decimal.Decimal('-1'), decimal.Decimal('1')}
# End program