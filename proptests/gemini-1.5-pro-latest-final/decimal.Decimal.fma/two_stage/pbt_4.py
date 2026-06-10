@given(st.data())
def test_decimal_Decimal_fma_output_scale(data):
    # Draw Decimal objects from the strategy.
    self = data.draw(decimals)
    other = data.draw(decimals)
    third = data.draw(decimals)

    # Assert that the output's scale is the maximum of the input scales.
    result = self.fma(other, third)
    expected_scale = max(self.as_tuple().exponent, other.as_tuple().exponent, third.as_tuple().exponent)
    assert result.as_tuple().exponent == expected_scale
# End program