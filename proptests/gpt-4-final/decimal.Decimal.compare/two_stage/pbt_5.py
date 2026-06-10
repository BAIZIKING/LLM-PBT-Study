from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False), st.decimals(allow_nan=False))
def test_normal_comparison(a, b):
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    if a < b:
        assert result == decimal.Decimal('-1')
    elif a == b:
        assert result == decimal.Decimal('0')
    elif a > b:
        assert result == decimal.Decimal('1')

@given(st.just(decimal.Decimal('NaN')), st.decimals())
def test_nan_first_input(a, b):
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    assert result == decimal.Decimal('NaN')

@given(st.decimals(), st.just(decimal.Decimal('NaN')))
def test_nan_second_input(a, b):
    result = decimal.Decimal(a).compare(decimal.Decimal(b))
    assert result == decimal.Decimal('NaN')

#given incorrect input type
@given(st.text(), st.text())
def test_string_input(a, b):
    try:
        decimal.Decimal(a).compare(decimal.Decimal(b))
        assert False, "Expected a TypeError here"
    except TypeError:
        pass

# End program