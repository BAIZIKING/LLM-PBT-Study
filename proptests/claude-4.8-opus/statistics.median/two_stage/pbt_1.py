from hypothesis import given, strategies as st
import statistics

# Strategy for numeric data: bounded floats (no nan/inf) and integers,
# kept within a reasonable range to avoid overflow issues.
numbers = st.one_of(
    st.integers(min_value=-10**9, max_value=10**9),
    st.floats(
        min_value=-1e9,
        max_value=1e9,
        allow_nan=False,
        allow_infinity=False,
    ),
)

nonempty_data = st.lists(numbers, min_size=1)


@given(data=nonempty_data)
def test_statistics_median_within_range():
    # Property 1: median is between min and max of the data.
    result = statistics.median(data)
    assert min(data) <= result <= max(data)
# End program


@given(data=nonempty_data, perm_seed=st.randoms(use_true_random=False))
def test_statistics_median_permutation_invariant():
    # Property 2: median invariant under permutation of input.
    shuffled = list(data)
    perm_seed.shuffle(shuffled)
    assert statistics.median(data) == statistics.median(shuffled)
# End program


@given(data=nonempty_data)
def test_statistics_median_odd_is_element():
    # Property 3: for odd-length data, median is an actual element.
    if len(data) % 2 == 1:
        result = statistics.median(data)
        assert result in data
        # Specifically the middle element of the sorted data.
        assert result == sorted(data)[len(data) // 2]
# End program


@given(data=nonempty_data)
def test_statistics_median_even_is_mean_of_middle():
    # Property 4: for even-length data, median is mean of two middle values.
    if len(data) % 2 == 0:
        result = statistics.median(data)
        s = sorted(data)
        mid = len(data) // 2
        expected = (s[mid - 1] + s[mid]) / 2
        assert result == expected
# End program


@given(
    data=nonempty_data,
    a=st.floats(
        min_value=0.001, max_value=1000,
        allow_nan=False, allow_infinity=False,
    ),
    b=st.floats(
        min_value=-1000, max_value=1000,
        allow_nan=False, allow_infinity=False,
    ),
)
def test_statistics_median_linear_equivariance():
    # Property 5: median(a*x + b) == a * median(x) + b for a > 0.
    transformed = [a * x + b for x in data]
    expected = a * statistics.median(data) + b
    result = statistics.median(transformed)
    # Use tolerance due to floating-point arithmetic.
    assert abs(result - expected) <= 1e-6 * (1 + abs(expected))
# End program