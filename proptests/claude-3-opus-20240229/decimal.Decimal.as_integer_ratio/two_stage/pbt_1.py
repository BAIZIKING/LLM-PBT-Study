from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_returns_tuple_of_integers(dec):
    n, d = dec.as_integer_ratio()
    assert isinstance(n, int) and isinstance(d, int)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_positive_denominator(dec):
    _, d = dec.as_integer_ratio()
    assert d > 0

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_lowest_terms(dec):
    n, d = dec.as_integer_ratio()
    assert decimal.Decimal(n).as_integer_ratio()[1] == 1

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio_equality(dec):
    n, d = dec.as_integer_ratio()
    assert dec == decimal.Decimal(n) / decimal.Decimal(d)

@given(st.sampled_from([decimal.Decimal('Infinity'), decimal.Decimal('-Infinity'), decimal.Decimal('NaN')]))
def test_decimal_as_integer_ratio_raises_exception(dec):
    try:
        dec.as_integer_ratio()
    except (OverflowError, ValueError):
        assert True
    else:
        assert False
# End program