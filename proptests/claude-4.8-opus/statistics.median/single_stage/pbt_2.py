from hypothesis import given, strategies as st
import statistics

# Summary: Generate non-empty lists of finite ints/floats (no NaN/inf) of varying
# sizes (odd/even, single element, duplicates, negatives); verify median is bounded
# by min/max, order-invariant, equals middle (odd) or mean-of-middle-two (even),
# and that empty data raises StatisticsError.
@given(st.data())
def test_statistics_median():
    # Empty input must raise StatisticsError
    try:
        statistics.median([])
        assert False, "Expected StatisticsError for empty data"
    except statistics.StatisticsError:
        pass

    numbers = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    data = st.data().draw(st.lists(numbers, min_size=1, max_size=50))

    result = statistics.median(data)
    s = sorted(data)
    n = len(s)

    # Property 1: median lies within [min, max]
    assert s[0] <= result <= s[-1]

    # Property 2: order invariance
    assert statistics.median(list(reversed(data))) == result

    # Property 3 & 4: exact value for odd vs even length
    if n % 2 == 1:
        assert result == s[n // 2]
    else:
        assert result == (s[n // 2 - 1] + s[n // 2]) / 2
# End program