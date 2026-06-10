from hypothesis import given, strategies as st
from statistics import correlation, StatisticsError

@given(st.data())
def test_statistics_correlation(data):
    list_length = data.draw(st.integers(min_value=2, max_value=1000))  # Ensure a minimum length of 2
    x = data.draw(st.lists(st.floats(), min_size=list_length, max_size=list_length))

    assert round(correlation(x, x), 2) == 1  # A list correlated with itself should be 1

    y = data.draw(st.lists(st.just(x[0]), min_size=list_length, max_size=list_length)) # This will create a list with all elements the same as the first element of x

    try:
        correlation(x,y)
        assert False, "Should have thrown an exception because y is a constant list"
    except StatisticsError:
        pass

    z = x.copy()
    z.reverse()

    if x[0] != x[1]: # If list is not constant
        assert round(correlation(x, z), 2) == -1  # A list correlated with its reverse should be -1 if the list is not constant

    try:
        correlation(x,x[:-1])
        assert False, "Should have thrown an exception because x and x[:-1] (x without last element) are of unequal lengths"
    except StatisticsError:
        pass

# End program