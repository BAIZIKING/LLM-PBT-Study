from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates diverse decimals and edge cases for fma inputs, checks accuracy and special value handling
@given(st.data())
def test_decimal_fma(data):
    # Generate diverse decimals for self, other, and third
    self_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    other_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))
    third_dec = data.draw(st.decimals(allow_nan=True, allow_infinity=True))

    # Calculate expected result with intermediate rounding
    expected = (self_dec * other_dec).quantize(Decimal("1E-10")) + third_dec

    # Get fma result
    result = Decimal.fma(self_dec, other_dec, third_dec)

    # Check accuracy (within a small tolerance)
    assert abs(result - expected) < Decimal("1E-20")

    # Check for special values (NaN and Infinity)
    if self_dec in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]:
        assert result in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]
    if other_dec in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]:
        assert result in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]
    if third_dec in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]:
        assert result in [Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]

# End program