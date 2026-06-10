from hypothesis import given, strategies as st
import statistics

fraction_values = st.fractions(
    min_value=-10**6,
    max_value=10**6,
    max_denominator=1000,
)

non_empty_fraction_lists = st.lists(
    fraction_values,
    min_size=1,
    max_size=50,
)


@given(st.data())
def test_statistics_mean_is_sum_divided_by_count(data):
    xs = data.draw(non_empty_fraction_lists)
    assert statistics.mean(xs) == sum(xs) / len(xs)


@given(st.data())
def test_statistics_mean_lies_between_minimum_and_maximum(data):
    xs = data.draw(non_empty_fraction_lists)
    result = statistics.mean(xs)
    assert min(xs) <= result <= max(xs)


@given(st.data())
def test_statistics_mean_is_invariant_under_reordering(data):
    xs = data.draw(st.lists(fraction_values, min_size=1, max_size=10))
    reordered = data.draw(st.permutations(xs))
    assert statistics.mean(xs) == statistics.mean(reordered)


@given(st.data())
def test_statistics_mean_shifts_when_constant_is_added(data):
    xs = data.draw(non_empty_fraction_lists)
    constant = data.draw(fraction_values)

    shifted = [x + constant for x in xs]

    assert statistics.mean(shifted) == statistics.mean(xs) + constant


@given(st.data())
def test_statistics_mean_scales_when_multiplied_by_constant(data):
    xs = data.draw(non_empty_fraction_lists)
    constant = data.draw(
        st.fractions(
            min_value=-1000,
            max_value=1000,
            max_denominator=100,
        )
    )

    scaled = [x * constant for x in xs]

    assert statistics.mean(scaled) == statistics.mean(xs) * constant

# End program