from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances within a reasonable range
def safe_decimals():
    return st.decimals(
        min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False
    )

@given(safe_decimals())
def test_denominator_is_positive(d):
    n, d = d.as_integer_ratio()
    assert d > 0

@given(safe_decimals())
def test_fraction_is_lowest_terms(d):
    n, d = d.as_integer_ratio()
    assert math.gcd(n, d) == 1

@given(safe_decimals())
def test_product_equals_original(d):
    n, d = d.as_integer_ratio()
    assert decimal.Decimal(n) / decimal.Decimal(d) == d

@given(safe_decimals())
def test_sign_matches(d):
    n, _ = d.as_integer_ratio()
    assert (n > 0 and d > 0) or (n < 0 and d < 0) or (n == 0 and d == 1)

@given(st.just(decimal.Decimal('NaN')))
def test_nan_raises_value_error(d):
    with pytest.raises(ValueError):
        d.as_integer_ratio()
# End program