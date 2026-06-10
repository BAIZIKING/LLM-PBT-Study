from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.data(), st.decimals(), st.decimals())
def test_decimal_fma(data, d1, d2):
    # strategy 1: decimal numbers
    self = data.draw(st.decimals())
    other = d1
    third = d2
    result = Decimal(self).fma(other, third)
    assert result == self*other + third and isinstance(result, Decimal)
    
    # strategy 2: integers
    self = data.draw(st.integers())
    other = int(d1)
    third = int(d2)
    result = Decimal(self).fma(other, third)
    assert result == self*other + third and isinstance(result, Decimal)
    
    # strategy 3: negative numbers
    self = data.draw(st.integers(min_value=-100, max_value=-1))
    other = -abs(int(d1))
    third = -abs(int(d2))
    result = Decimal(self).fma(other, third)
    assert result == self*other + third and isinstance(result, Decimal)