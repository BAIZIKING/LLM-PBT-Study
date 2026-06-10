from hypothesis import given, strategies as st
import statistics

fraction_values = st.fractions(
    min_value=-10_000,
    max_value=10_000,
    max_denominator=1_000,
)

fraction_lists = st.lists(
    fraction_values,
    min_size=2,
    max_size=50,
)


@given(fraction_lists)
def test_statistics_variance_matches_definition(data):
    mean = statistics.mean(data)
    expected = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    assert statistics.variance(data) == expected
    assert statistics.variance(data, None) == expected


@given(fraction_lists)
def test_statistics_variance_is_non_negative(data):
    mean = statistics.mean(data)
    assert statistics.variance(data) >= 0
    assert statistics.variance(data, mean) >= 0


@given(fraction_lists)
def test_statistics_variance_is_zero_iff_all_values_equal(data):
    variance = statistics.variance(data)
    all_equal = all(x == data[0] for x in data)
    assert (variance == 0) == all_equal


@given(fraction_lists, fraction_values)
def test_statistics_variance_is_translation_invariant(data, shift):
    shifted_data = [x + shift for x in data]
    assert statistics.variance(shifted_data) == statistics.variance(data)


@given(fraction_lists, st.fractions(min_value=-100, max_value=100, max_denominator=100))
def test_statistics_variance_scales_quadratically(data, scale):
    scaled_data = [scale * x for x in data]
    assert statistics.variance(scaled_data) == scale ** 2 * statistics.variance(data)


# End program