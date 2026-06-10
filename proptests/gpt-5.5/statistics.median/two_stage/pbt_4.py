from hypothesis import given, strategies as st
import statistics

bounded_ints = st.integers(min_value=-10**12, max_value=10**12)


@given(st.lists(bounded_ints, min_size=1, max_size=100))
def test_statistics_median_is_between_minimum_and_maximum(data):
    result = statistics.median(data)
    assert min(data) <= result <= max(data)


@given(st.data())
def test_statistics_median_is_invariant_under_reordering(draw_data):
    data = draw_data.draw(st.lists(bounded_ints, min_size=1, max_size=100))
    reordered = draw_data.draw(st.permutations(data))
    assert statistics.median(data) == statistics.median(reordered)


@given(st.data())
def test_statistics_median_odd_length_is_middle_sorted_value(draw_data):
    half_length = draw_data.draw(st.integers(min_value=0, max_value=50))
    data = draw_data.draw(
        st.lists(bounded_ints, min_size=2 * half_length + 1, max_size=2 * half_length + 1)
    )

    sorted_data = sorted(data)
    assert statistics.median(data) == sorted_data[half_length]


@given(st.data())
def test_statistics_median_even_length_is_mean_of_two_middle_sorted_values(draw_data):
    half_length = draw_data.draw(st.integers(min_value=1, max_value=50))
    data = draw_data.draw(
        st.lists(bounded_ints, min_size=2 * half_length, max_size=2 * half_length)
    )

    sorted_data = sorted(data)
    expected = (sorted_data[half_length - 1] + sorted_data[half_length]) / 2
    assert statistics.median(data) == expected


@given(
    st.lists(
        st.integers(min_value=-10**9, max_value=10**9),
        min_size=1,
        max_size=100,
    ),
    st.integers(min_value=-10**9, max_value=10**9),
)
def test_statistics_median_shifts_by_added_constant(data, constant):
    shifted_data = [value + constant for value in data]
    assert statistics.median(shifted_data) == statistics.median(data) + constant


# End program