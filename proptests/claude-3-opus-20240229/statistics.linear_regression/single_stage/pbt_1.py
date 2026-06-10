from hypothesis import given, strategies as st
import statistics

# Summary:
# Generate lists x and y of variable length >= 2 containing floats
# Sometimes generate constant values in x to test error handling
# Toggle proportional between True and False
# Ensure x and y are the same length
@given(st.data())
def test_statistics_linear_regression(data):
    n = data.draw(st.integers(min_value=2, max_value=100))
    x = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n))
    if data.draw(st.booleans()):
        x = [data.draw(st.floats(allow_nan=False, allow_infinity=False))] * n
    y = data.draw(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=n, max_size=n))
    proportional = data.draw(st.booleans())

    try:
        slope, intercept = statistics.linear_regression(x, y, proportional=proportional)
        assert isinstance(slope, float)
        assert isinstance(intercept, float)
        if proportional:
            assert intercept == 0
    except statistics.StatisticsError:
        assert len(set(x)) == 1
    else:
        assert len(x) == len(y) >= 2
# End program