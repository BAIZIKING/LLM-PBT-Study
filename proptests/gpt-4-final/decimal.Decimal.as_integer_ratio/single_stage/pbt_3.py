from hypothesis import given, strategies as st
from hypothesis.extra import numpy as npst
from decimal import Decimal, getcontext
from hypothesis import settings
from math import isinf, isnan

# Ensure enough precision
getcontext().prec = 50

@given(st.decimals(allow_infinity=False, allow_nan=False).map(Decimal))
def test_decimal_as_integer_ratio(decimal_value):
    n, d = decimal_value.as_integer_ratio()

    # check that the ratio equals to the original value within a small tolerance
    st.floats(also_edge_cases=False).map(isinf).assume(n)
    st.floats(also_edge_cases=False).map(isinf).assume(d)
    st.floats(also_edge_cases=False).map(isnan).assume(n)
    st.floats(also_edge_cases=False).map(isnan).assume(d)
    assert n / d == decimal_value
# End program