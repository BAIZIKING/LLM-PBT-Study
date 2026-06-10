from hypothesis import given, strategies as st, assume
from statistics import correlation, StatisticsError

@given(st.data())
def test_statistics_correlation(data):
    n = data.draw(st.integers(min_value=2, max_value=1000))  # length of lists
    # Generating two lists of the same length and not constant
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n))
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n))
    # Generating the 'method' parameter
    method = data.draw(st.sampled_from(['linear', 'ranked']))
    assume(x != n*[x[0]] and y != n*[y[0]])  # ensuring the inputs are not constant

    try:
        # Checking if the returned correlation coefficient is between -1 and +1
        assert -1 <= correlation(x, y, method=method) <= 1
    except StatisticsError as e:
        # Checking if the error message is correct
        assert str(e) == 'inputs must be of the same length and not constant'
# End program