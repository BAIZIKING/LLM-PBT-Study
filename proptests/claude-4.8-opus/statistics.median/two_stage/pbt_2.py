from hypothesis import given, strategies as st
import statistics
import math

# Strategy for numeric values that avoids overflow and NaN/inf issues
finite_numbers = st.one_of(
    st.integers(min_value=-10**9, max_value=10**9),
    st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False)
)

nonempty_data = st.lists(finite_numbers, min_size=1)


@given(data=nonempty_data)
def test_statistics_median_within_range(data):
    # Property 1: median is within [min, max] of the data
    result = statistics.median(data)
    assert min(data) <= result <= max(data)


@given(data=nonempty_data, perm_seed=st.randoms())
def test_statistics_median_permutation_invariant(data, perm_seed):
    # Property 2: median invariant under permutation
    shuffled = list(data)
    perm_seed.shuffle(shuffled)
    assert statistics.median(data) == statistics.median(shuffled)


@given(data=nonempty_data)
def test_statistics_median_odd_is_element(data):
    # Property 3: for odd-length data, median is an actual element
    if len(data) % 2 == 1:
        result = statistics.median(data)
        assert result in data


@given(data=nonempty_data)
def test_statistics_median_even_is_average(data):
    # Property 4: for even-length data, median is average of two middle values
    if len(data) % 2 == 0:
        result = statistics.median(data)
        s = sorted(data)
        mid = len(s) // 2
        expected = (s[mid - 1] + s[mid]) / 2
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)


@given(
    data=nonempty_data,
    scale=st.floats(min_value=0.001, max_value=1000, allow_nan=False, allow_infinity=False),
    shift=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
)
def test_statistics_median_linear_transformation(data, scale, shift):
    # Property 5: linear transformation of data scales/shifts the median accordingly
    original = statistics.median(data)
    transformed_data = [x * scale + shift for x in data]
    transformed_median = statistics.median(transformed_data)
    expected = original * scale + shift
    assert math.isclose(transformed_median, expected, rel_tol=1e-6, abs_tol=1e-6)
# End program