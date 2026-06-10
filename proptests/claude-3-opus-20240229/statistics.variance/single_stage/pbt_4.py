from hypothesis import given, strategies as st
from statistics import variance
from math import isclose

# Generate a wide variety of numeric lists to test variance. Key points:
# - Lists must have at least 2 elements, but can be arbitrarily long
# - Elements can be floats, ints, decimals or fractions 
# - Some lists with 0 variance (all elements equal)
# - Optionally generate xbar to pass as argument
@given(st.data())
def test_variance(data):
    elements = data.draw(st.one_of(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
        st.lists(st.integers(), min_size=2),
        st.lists(st.decimals(allow_nan=False, allow_infinity=False), min_size=2),
        st.lists(st.fractions(), min_size=2)
    ))

    xbar = data.draw(st.one_of(st.none(), st.just(sum(elements)/len(elements)))) 

    var = variance(elements, xbar)
    
    # Variance is always non-negative 
    assert var >= 0

    # Variance of elements all equal is 0
    if len(set(elements)) == 1:
        assert isclose(var, 0)

    # Passing correct xbar gives same result as default
    if xbar is not None:
        assert variance(elements, xbar) == variance(elements)
# End program        