from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances, avoiding overflows
def decimals():
    return st.decimals(
        min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
    )


@given(decimals())
def test_denominator_positive(d):
    n, d = d.as_integer_ratio()
    assert d > 0
# End program


@given(decimals())
def test_lowest_terms(d):
    n, d = d.as_integer_ratio()
    assert math.gcd(n, d) == 1 
# End program


@given(decimals())
def test_equivalent_value(d):
    n, d = d.as_integer_ratio()
    assert decimal.Decimal(n) / decimal.Decimal(d) == d
# End program


@given(decimals())
def test_sign_matches(d):
    n, _ = d.as_integer_ratio()
    assert (n >= 0) == (d >= 0)
# End program


@given(st.just(decimal.Decimal('inf')), st.just(decimal.Decimal('-inf')))
def test_overflow_behavior(d):
    with pytest.raises(OverflowError):
        d.as_integer_ratio()
# End program