from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_statistics_variance(data):
    # Property 1: Variance of a list with two or more element should not raise a StatisticsError
    try:
        res = statistics.variance(data)
    except statistics.StatisticsError:
        assert False, "Variance Calculation raised StatisticsError"

    # Property 2: Variance of the same list with and without xbar parameter should be same.
    m = statistics.mean(data)
    assert statistics.variance(data, m) == res, "Variance Calculation with xbar differs"

    # Property 3: Variance should always be a non-negative value.
    assert res >= 0, "Variance Calculation is negative"