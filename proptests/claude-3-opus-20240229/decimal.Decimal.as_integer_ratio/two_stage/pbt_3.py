from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_tuple_of_integers(dec):
    n, d = dec.as_integer_ratio()
    assert isinstance(n, int) and isinstance(d, int)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_positive_denominator(dec):
    _, d = dec.as_integer_ratio()
    assert d > 0

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_fraction_in_lowest_terms(dec):
    n, d = dec.as_integer_ratio()
    assert decimal.Decimal(n).as_integer_ratio() == (n, d)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_equal_fraction(dec):
    n, d = dec.as_integer_ratio()
    assert decimal.Decimal(n) / decimal.Decimal(d) == dec

@given(st.sampled_from([decimal.Decimal('Infinity'), decimal.Decimal('-Infinity'), decimal.Decimal('NaN')]))
def test_as_integer_ratio_raises_exception_on_special_values(dec):
    try:
        dec.as_integer_ratio()
        assert False, "Expected an exception to be raised"
    except (OverflowError, ValueError):
        pass
# End program