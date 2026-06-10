from hypothesis import given, strategies as st
import statistics
import math

# Strategy for finite, reasonably-bounded numeric values to avoid overflow
# and floating point precision issues.
numbers = st.one_of(
    st.integers(min_value=-10**9, max_value=10**9),
    st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False),
)

nonempty_lists = st.lists(numbers, min_size=1, max_size=100)


@given(data=nonempty_lists)
def test_statistics_median_within_range(data):
    # Property 1: The median is within [min(data), max(data)].
    result = statistics.median(data)
    assert min(data) <= result <= max(data)
# End program


@given(data=nonempty_lists, perm_seed=st.randoms(use_true_random=False))
def test_statistics_median_permutation_invariant(data, perm_seed):
    # Property 2: The median is invariant under permutation of the input.
    shuffled = data[:]
    perm_seed.shuffle(shuffled)
    original = statistics.median(data)
    permuted = statistics.median(shuffled)
    assert math.isclose(original, permuted, rel_tol=1e-9, abs_tol=1e-9)
# End program


@given(data=nonempty_lists)
def test_statistics_median_odd_is_member(data):
    # Property 3: For odd-length data, the median is an actual member of the data.
    if len(data) % 2 == 1:
        result = statistics.median(data)
        assert result in data
# End program


@given(data=nonempty_lists)
def test_statistics_median_even_is_average_of_middles(data):
    # Property 4: For even-length data, the median equals the average of the
    # two middle values of the sorted data.
    if len(data) % 2 == 0:
        s = sorted(data)
        n = len(s)
        expected = (s[n // 2 - 1] + s[n // 2]) / 2
        result = statistics.median(data)
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)
# End program


@given(
    data=nonempty_lists,
    offset=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    scale=st.floats(min_value=0.001, max_value=1e3, allow_nan=False, allow_infinity=False),
)
def test_statistics_median_shift_and_scale(data, offset, scale):
    # Property 5: Shifting all elements by a constant shifts the median by
    # that constant; scaling by a positive constant scales the median.
    base = statistics.median(data)

    shifted = [x + offset for x in data]
    shifted_median = statistics.median(shifted)
    assert math.isclose(shifted_median, base + offset, rel_tol=1e-6, abs_tol=1e-6)

    scaled = [x * scale for x in data]
    scaled_median = statistics.median(scaled)
    assert math.isclose(scaled_median, base * scale, rel_tol=1e-6, abs_tol=1e-6)
# End program