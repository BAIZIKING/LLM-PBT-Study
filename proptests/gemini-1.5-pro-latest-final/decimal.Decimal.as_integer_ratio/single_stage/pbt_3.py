from hypothesis import given, strategies as st, assume
import decimal

# Summary: Generates diverse decimals and edge cases to test as_integer_ratio
@given(st.data())
def test_decimal_as_integer_ratio(data):
    # Generate random decimals and include edge cases
    decimal_input = data.draw(st.one_of(
        st.decimals(),
        st.integers().map(decimal.Decimal),
        st.just(decimal.Decimal('NaN')),
        st.just(decimal.Decimal('Infinity'))
    ))

    # Handle exceptions for NaN and Infinity
    assume(not decimal_input.is_nan())
    assume(not decimal_input.is_infinite())

    n, d = decimal_input.as_integer_ratio()

    # Check exact conversion, lowest terms, and positive denominator
    assert decimal.Decimal(n) / d == decimal_input
    assert math.gcd(n, d) == 1
    assert d > 0
# End program