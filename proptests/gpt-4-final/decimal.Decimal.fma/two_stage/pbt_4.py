from hypothesis import given, strategies as st
from decimal import Decimal

# Test for Property 1: Self and Other Commutativity
@given(st.decimals(), st.decimals(), st.decimals())
def test_fma_self_other_commutativity(a, b, c):
    assert Decimal(a).fma(b, c) == Decimal(b).fma(a, c)

# Test for Property 2: Third and Other Association
@given(st.decimals(), st.decimals(), st.decimals())
def test_fma_third_other_association(a, b, c):
    assert Decimal(a).fma(b, c) == Decimal(a).fma(c, b)

# Test for Property 3: Self Neutral Element and Other Neutral Element
@given(st.decimals(), st.decimals())
def test_fma_self_other_neutral_element(a, b):
    assert Decimal(a).fma(1, 0) == Decimal(a)
    assert Decimal(1).fma(a, b) == Decimal(a + b)
  
# Test for Property 4: Distributivity
@given(st.decimals(), st.decimals(), st.decimals(), st.decimals())
def test_fma_distributivity(a, b, x, y):
    assert Decimal(a + b).fma(x + y, 0) == Decimal(a).fma(x, Decimal(b).fma(y, 0))

# Test for Property 5: Consistency across similar operations
@given(st.decimals(), st.decimals(), st.decimals())
def test_fma_consistency(a, b, c):
    assert Decimal(a).fma(b, c) == Decimal(a * b + c)
# End program