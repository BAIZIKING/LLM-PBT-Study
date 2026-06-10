from hypothesis import given, strategies as st
import statistics

# Summary: Generate empty and non-empty finite numeric iterables with varied lengths, odd/even sizes, duplicates, negatives, ints, floats, and fractions; wrap them as lists, tuples, or one-shot iterators. Check that empty input raises StatisticsError, odd-length input returns the sorted middle value, and even-length input returns the mean of the two sorted middle values.
@given(st.data())
def test_statistics_median(data):
    numeric = st.one_of(
        st.integers(min_value=-(10**300), max_value=10**300),
        st.floats(allow_nan=False, allow_infinity=False),
        st.fractions(max_denominator=1000),
    )

    values = data.draw(st.lists(numeric, min_size=0, max_size=50))
    wrapper = data.draw(st.sampled_from(["list", "tuple", "iter"]))

    if wrapper == "list":
        input_data = list(values)
    elif wrapper == "tuple":
        input_data = tuple(values)
    else:
        input_data = iter(values)

    if not values:
        try:
            statistics.median(input_data)
        except statistics.StatisticsError:
            return
        assert False, "median() should raise StatisticsError for empty data"

    result = statistics.median(input_data)
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2

    if n % 2 == 1:
        expected = sorted_values[mid]
    else:
        expected = (sorted_values[mid - 1] + sorted_values[mid]) / 2

    assert result == expected
# End program