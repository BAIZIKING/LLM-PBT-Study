from hypothesis import given, strategies as st
import statistics
from fractions import Fraction

fraction_values = st.fractions(
    min_value=Fraction(-1000),
    max_value=Fraction(1000),
    max_denominator=1000,
)

data_values = st.lists(
    fraction_values,
    min_size=2,
    max_size=50,
)


@given(data_values)
def test_statistics_variance_is_non_negative(data):
    result = statistics.variance(data)
    assert result >= 0


@given(data_values)
def test_statistics_variance_matches_sum_of_squared_deviations(data):
    mean = statistics.mean(data)
    expected = sum((x - mean) ** 2 for x in data) / (len(data) - 1)

    assert statistics.variance(data) == expected
    assert statistics.variance(data, mean) == expected


@given(data_values)
def test_statistics_variance_is_zero_iff_all_values_are_equal(data):
    result = statistics.variance(data)
    all_equal = all(x == data[0] for x in data)

    assert (result == 0) == all_equal


@given(data_values, fraction_values)
def test_statistics_variance_is_translation_invariant(data, offset):
    shifted_data = [x + offset for x in data]

    assert statistics.variance(shifted_data) == statistics.variance(data)


@given(data_values, fraction_values)
def test_statistics_variance_scales_quadratically(data, scale):
    scaled_data = [scale * x for x in data]

    assert statistics.variance(scaled_data) == scale ** 2 * statistics.variance(data)


# End program