from hypothesis import given, strategies as st
import statistics
from fractions import Fraction

bounded_fractions = st.fractions(
    min_value=Fraction(-10**6),
    max_value=Fraction(10**6),
    max_denominator=1000,
)

bounded_fraction_lists = st.lists(
    bounded_fractions,
    min_size=1,
    max_size=100,
)


@given(st.data())
def test_statistics_mean_equals_sum_divided_by_count(data):
    values = data.draw(bounded_fraction_lists)

    result = statistics.mean(values)
    expected = sum(values, Fraction(0)) / len(values)

    assert result == expected


@given(st.data())
def test_statistics_mean_is_between_minimum_and_maximum(data):
    values = data.draw(bounded_fraction_lists)

    result = statistics.mean(values)

    assert min(values) <= result <= max(values)


@given(st.data())
def test_statistics_mean_is_independent_of_input_order(data):
    values = data.draw(bounded_fraction_lists)
    reordered_values = data.draw(st.permutations(values))

    assert statistics.mean(values) == statistics.mean(reordered_values)


@given(st.data())
def test_statistics_mean_shifts_by_added_constant(data):
    values = data.draw(bounded_fraction_lists)
    constant = data.draw(bounded_fractions)

    shifted_values = [value + constant for value in values]

    assert statistics.mean(shifted_values) == statistics.mean(values) + constant


@given(st.data())
def test_statistics_mean_scales_by_multiplicative_factor(data):
    values = data.draw(bounded_fraction_lists)
    factor = data.draw(bounded_fractions)

    scaled_values = [value * factor for value in values]

    assert statistics.mean(scaled_values) == statistics.mean(values) * factor


# End program