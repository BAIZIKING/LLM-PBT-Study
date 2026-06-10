from hypothesis import given, strategies as st
import statistics

SAFE_INTS = st.integers(min_value=-10**6, max_value=10**6)


@given(st.data())
def test_statistics_median_is_between_minimum_and_maximum(data):
    values = data.draw(st.lists(SAFE_INTS, min_size=1, max_size=100))

    result = statistics.median(values)

    assert min(values) <= result <= max(values)


@given(st.data())
def test_statistics_median_is_unchanged_by_reordering(data):
    values = data.draw(st.lists(SAFE_INTS, min_size=1, max_size=100))
    reordered = data.draw(st.permutations(values))

    assert statistics.median(values) == statistics.median(reordered)


@given(st.data())
def test_statistics_median_of_odd_length_data_is_middle_sorted_value(data):
    half_size = data.draw(st.integers(min_value=0, max_value=50))
    size = 2 * half_size + 1
    values = data.draw(st.lists(SAFE_INTS, min_size=size, max_size=size))

    sorted_values = sorted(values)
    expected = sorted_values[half_size]

    assert statistics.median(values) == expected
    assert statistics.median(values) in values


@given(st.data())
def test_statistics_median_of_even_length_data_is_mean_of_middle_sorted_values(data):
    half_size = data.draw(st.integers(min_value=1, max_value=50))
    size = 2 * half_size
    values = data.draw(st.lists(SAFE_INTS, min_size=size, max_size=size))

    sorted_values = sorted(values)
    expected = (sorted_values[half_size - 1] + sorted_values[half_size]) / 2

    assert statistics.median(values) == expected


@given(st.data())
def test_statistics_median_shifts_by_added_constant(data):
    values = data.draw(st.lists(SAFE_INTS, min_size=1, max_size=100))
    offset = data.draw(SAFE_INTS)

    shifted_values = [value + offset for value in values]

    assert statistics.median(shifted_values) == statistics.median(values) + offset


# End program