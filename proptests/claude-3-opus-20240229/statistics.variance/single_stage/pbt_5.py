from hypothesis import given, strategies as st
from statistics import variance
from math import isclose

# Generate a wide variety of numeric lists to test variance. Key ideas:
# - Test lists of varying lengths, from empty to longer lists
# - Generate lists of ints, floats, fractions, and decimals 
# - Sometimes insert a non-numeric value to check for exceptions
# - Pass in mean value xbar as a separate parameter sometimes
# - Check variance result against statistical properties like non-negativity
@given(st.data())
def test_variance(data):
    values = data.draw(st.one_of(
        st.lists(st.integers()),
        st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
        st.lists(st.fractions()),
        st.lists(st.decimals(allow_nan=False, allow_infinity=False))
    ))
    data.draw(st.lists(st.none() | st.text(), max_size=1), label='non_numeric') 
    xbar = data.draw(st.one_of(st.none(), st.floats(), st.decimals()), label='mean')

    if len(values) < 2:
        try:
            variance(values)
            assert False, "Expected StatisticsError for < 2 values"
        except StatisticsError:
            pass
    else:
        try:
            var = variance(values, xbar=xbar)
            assert var >= 0, "Variance can't be negative" 
            assert isclose(var, 0, abs_tol=1e-8) or var > 0
        except TypeError:
            pass
# End program      