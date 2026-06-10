from hypothesis import given, strategies as st
import statistics

# Summary: Generate non-empty lists of finite numbers (ints and floats mixed),
# letting Hypothesis explore single elements, duplicates, negatives, and extreme
# values. Check that the median lies within [min, max], matches the sorted-middle
# definition for odd/even lengths, and is invariant under input ordering.
@given(st.data())
def test_statistics_median(data):
    numbers = data.draw(
        st.lists(
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
            ),
            min_size=1,
        )
    )

    result = statistics.median(numbers)
    ordered = sorted(numbers)
    n = len(ordered)

    # Property 1: median lies within [min, max]
    assert ordered[0] <= result <= ordered[-1]

    # Property 2 & 3: matches the sorted-middle definition
    if n % 2 == 1:
        expected = ordered[n // 2]
        assert result == expected
        # odd-length median is an actual data point
        assert result in numbers
    else:
        expected = (ordered[n // 2 - 1] + ordered[n // 2]) / 2
        assert result == expected

    # Property 4: permutation invariance (order should not matter)
    assert statistics.median(ordered) == result
# End program