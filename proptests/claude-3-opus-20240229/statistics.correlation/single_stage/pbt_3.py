from hypothesis import given, strategies as st
from statistics import correlation
from math import isclose

# Summary: 
# - Generate two equal-length lists of floats or ints with length >= 2
# - Try different edge cases like very large/small numbers, many repeated values, NaNs, +/- infinity
# - Check that output is between -1 and 1 inclusive
# - Check that swapping input order doesn't change output
# - Check that multiplying inputs by a constant doesn't change output
# - Check that adding a constant to the inputs doesn't change the output
# - Check that computing the correlation of an input with itself returns 1.0
# - Check that Spearman correlation is 1.0 for monotonically increasing inputs
@given(st.lists(st.floats() | st.integers(), min_size=2).flatmap(lambda x: st.tuples(st.just(x), st.just(x))))
def test_statistics_correlation(inputs):
    x, y = inputs
    result1 = correlation(x, y)
    result2 = correlation(y, x)
    result3 = correlation([a * 1e10 for a in x], [b * 1e10 for b in y]) 
    result4 = correlation([a + 1e10 for a in x], [b + 1e10 for b in y])
    result5 = correlation(x, x)

    assert -1 <= result1 <= 1
    assert isclose(result1, result2)
    assert isclose(result1, result3) 
    assert isclose(result1, result4)
    assert isclose(result5, 1.0)

    if all(a < b for a, b in zip(x, x[1:])):
        assert isclose(correlation(x, x, method='ranked'), 1.0)
# End program        