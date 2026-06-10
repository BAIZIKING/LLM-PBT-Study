from hypothesis import given, strategies as st
import statistics

finite_numbers = st.fractions(
    min_value=-10_000,
    max_value=10_000,
    max_denominator=1_000,
)

data_samples = st.lists(
    finite_numbers,
    min_size=2,
    max_size=50,
)


@given(data_samples)
def test_statistics_variance_is_non_negative(data):
    assert statistics.variance(data) >= 0


@given(data_samples)
def test_statistics_variance_zero_iff_all_values_equal(data):
    result = statistics.variance(data)

    if all(x == data[0] for x in data):
        assert result == 0
    else:
        assert result > 0


@given(data_samples, finite_numbers)
def test_statistics_variance_is_translation_invariant(data, shift):
    shifted_data = [x + shift for x in data]

    assert statistics.variance(shifted_data) == statistics.variance(data)


@given(data_samples, finite_numbers)
def test_statistics_variance_scales_quadratically(data, scale):
    scaled_data = [x * scale for x in data]

    assert statistics.variance(scaled_data) == statistics.variance(data) * scale * scale


@given(data_samples)
def test_statistics_variance_with_true_xbar_matches_default(data):
    xbar = statistics.mean(data)

    assert statistics.variance(data, xbar) == statistics.variance(data)


# End program