from hypothesis import given, strategies as st
import statistics

# Summary: Generate non-empty lists of numeric values (ints and finite floats),
# mixing types and sizes to cover odd/even lengths, duplicates, negatives, and
# single-element edge cases. Check that the median lies within [min, max], is
# invariant under shuffling, and matches the sorted-middle definition for both
# odd-length (exact middle element) and even-length (average of two middles) data.
@given(st.data())
def test_statistics_median(data):
    numeric = st.one_of(
        st.integers(min_value=-10**9, max_value=10**9),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e9, max_value=1e9),
    )
    values = data.draw(st.lists(numeric, min_size=1, max_size=50))

    result = statistics.median(values)

    # Property 1: median lies within [min, max]
    assert min(values) <= result <= max(values)

    # Property 2: order independence (invariant under shuffling)
    shuffled = data.draw(st.permutations(values))
    assert statistics.median(shuffled) == result

    # Properties 3 & 4: matches sorted-middle definition
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        assert result == s[n // 2]
    else:
        expected = (s[n // 2 - 1] + s[n // 2]) / 2
        assert result == expected
# End program