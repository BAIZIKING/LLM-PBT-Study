from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_returns_tuple_of_integers(dec):
    ratio = dec.as_integer_ratio()
    assert isinstance(ratio, tuple)
    assert len(ratio) == 2
    assert isinstance(ratio[0], int)
    assert isinstance(ratio[1], int)

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_positive_denominator(dec):
    ratio = dec.as_integer_ratio()
    assert ratio[1] > 0

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_lowest_terms(dec):
    ratio = dec.as_integer_ratio()
    n, d = ratio
    assert math.gcd(n, d) == 1

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_as_integer_ratio_numerical_equivalence(dec):
    ratio = dec.as_integer_ratio()
    n, d = ratio
    assert decimal.Decimal(n) / decimal.Decimal(d) == dec

@given(st.decimals(allow_nan=True, allow_infinity=True))
def test_as_integer_ratio_raises_exceptions(dec):
    if dec.is_infinite():
        with pytest.raises(OverflowError):
            dec.as_integer_ratio()
    elif dec.is_nan():
        with pytest.raises(ValueError):
            dec.as_integer_ratio()
    else:
        ratio = dec.as_integer_ratio()
        assert isinstance(ratio, tuple)
# End program