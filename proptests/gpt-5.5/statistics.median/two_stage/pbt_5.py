from hypothesis import given, strategies as st
import statistics

SAFE_NUMBERS = st.one_of(
    st.integers(min_value=-(10**12), max_value=10**12),
    st.floats(
        min_value=-1e12,
        max_value=1e12,
        allow_nan=False,
        allow_infinity=False,
        width=64,
    ),
)

@given(st.data())
def test_statistics_median_permutation_invariant_property(data):
    values = data.draw(st.lists(SAFE_NUMBERS, min_size=1, max_size=8))
    permuted = data.draw(st.permutations(values))

    assert statistics.median(values) == statistics.median(permuted)

@given(st.data())
def test_statistics_median_odd_length_middle_value_property(data):
    half_size = data.draw(st.integers(min_value=0, max_value=50))
    size = 2 * half_size + 1
    values = data.draw(st.lists(SAFE_NUMBERS, min_size=size, max_size=size))

    ordered = sorted(values)

    assert statistics.median(values) == ordered[half_size]

@given(st.data())
def test_statistics_median_even_length_mean_of_middle_values_property(data):
    half_size = data.draw(st.integers(min_value=1, max_value=50))
    size = 2 * half_size
    values = data.draw(st.lists(SAFE_NUMBERS, min_size=size, max_size=size))

    ordered = sorted(values)
    expected = (ordered[half_size - 1] + ordered[half_size]) / 2

    assert statistics.median(values) == expected

@given(st.data())
def test_statistics_median_between_minimum_and_maximum_property(data):
    values = data.draw(st.lists(SAFE_NUMBERS, min_size=1, max_size=100))

    result = statistics.median(values)

    assert min(values) <= result <= max(values)

@given(st.data())
def test_statistics_median_empty_input_raises_statistics_error_property(data):
    try:
        statistics.median([])
    except statistics.StatisticsError:
        pass
    else:
        assert False
# End program