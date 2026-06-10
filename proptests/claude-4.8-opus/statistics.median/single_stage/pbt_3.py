from hypothesis import given, strategies as st
import statistics
from statistics import StatisticsError

# Summary: Generate non-empty lists of finite numeric values (ints and floats),
# covering odd/even lengths, duplicates, negatives, and single-element cases.
# Check that the median lies within [min, max], is order-invariant, equals the
# middle sorted element for odd lengths, equals the mean of the two middle
# sorted values for even lengths, and that empty input raises StatisticsError.
@given(st.data())
def test_statistics_median():
    numbers = st.one_of(
        st.integers(min_value=-10**6, max_value=10**6),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e9, max_value=1e9),
    )
    drawer = st.data()

    # Empty input must raise StatisticsError
    try:
        statistics.median([])
        assert False, "Expected StatisticsError for empty data"
    except StatisticsError:
        pass

    # Draw a non-empty list of numeric values
    data = drawer.draw(st.lists(numbers, min_size=1, max_size=50))

    result = statistics.median(data)
    s = sorted(data)
    n = len(s)

    # Property 1: median lies within the data bounds
    assert s[0] <= result <= s[-1]

    # Property 2: order-invariance (shuffled input yields same median)
    shuffled = drawer.draw(st.permutations(data))
    assert statistics.median(shuffled) == result

    # Property 3 & 4: odd vs even computation rules
    if n % 2 == 1:
        # odd: median is the actual middle element
        assert result == s[n // 2]
    else:
        # even: median is the average of the two middle values
        expected = (s[n // 2 - 1] + s[n // 2]) / 2
        assert result == expected
# End program