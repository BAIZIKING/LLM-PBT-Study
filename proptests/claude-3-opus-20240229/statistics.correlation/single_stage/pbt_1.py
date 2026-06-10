from hypothesis import given, strategies as st
from statistics import correlation
from math import isclose

# Generate a variety of input lists for statistics.correlation:
# - Use the 'data()' strategy to compose sub-strategies
# - Lists should have at least 2 elements to avoid StatisticsError 
# - Generate both integer and floating point lists
# - Sometimes generate two equal length lists, other times different lengths
# - Test edge cases like empty lists, very large/small numbers, infinities, and NaNs
@given(st.data())
def test_correlation(data):
    elements = data.draw(st.one_of(st.integers(), st.floats(allow_infinity=True, allow_nan=True)))
    x = data.draw(st.lists(elements, min_size=2))
    y = data.draw(st.lists(elements, min_size=0, max_size=len(x))) 
    
    try:
        result = correlation(x, y)
        # Pearson correlation is between -1 and 1
        assert -1 <= result <= 1
        # Correlation with itself is 1
        assert isclose(correlation(x, x), 1.0)
        # Correlation is symmetric
        assert isclose(correlation(x, y), correlation(y, x))

    except StatisticsError:
        # Validate StatisticsError for lists under length 2
        assert len(x) < 2 or len(y) < 2
        # Validate StatisticsError for unequal length lists  
        assert len(x) != len(y)
# End program