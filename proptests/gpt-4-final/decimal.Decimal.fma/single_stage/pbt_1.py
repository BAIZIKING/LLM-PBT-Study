from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.data())
def test_decimal_fma(data):
    # transforming the randomly generated floats to decimal
    self_n = Decimal(str(data.draw(st.floats())))
    other = Decimal(str(data.draw(st.floats())))
    third = Decimal(str(data.draw(st.floats())))

    # Performing the operation and comparing the result.
    res = self_n.fma(other, third)
    # To accurately compare floating point values, we round the results to a reasonable precision.
    assert round(res, 5) == round(self_n*other + third, 5)