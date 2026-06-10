from hypothesis import given, strategies as st
import statistics

# Summary: Generate non-empty lists of finite numeric values (ints and floats,
# excluding NaN/inf) of varying sizes, covering odd/even lengths, duplicates,
# negatives, and single-element edge cases. Verify the median lies within
# [min, max], is order-independent, and matches the manual definition
# (middle element for odd length, mean of two middle elements for even length).
@given(st.data())
def test_statistics_median(data):
    numbers = st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
    )
    values = data.draw(st.lists(numbers, min_size=1))

    result = statistics.median(values)

    # Property 1: median is within the bounds of the data
    assert min(values) <= result <= max(values)

    # Property 2: order independence
    assert result == statistics.median(sorted(values))
    assert result == statistics.median(list(reversed(values)))

    # Properties 3 & 4: matches manual definition
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        # odd length: exact middle element
        assert result == s[mid]
    else:
        # even length: average of two middle values
        assert result == (s[mid - 1] + s[mid]) / 2

    # Property 5 (special case of 3): single element
    if n == 1:
        assert result == values[0]
# End program