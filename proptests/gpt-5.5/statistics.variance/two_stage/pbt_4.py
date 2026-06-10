from hypothesis import given, strategies as st
import statistics

finite_numbers = st.fractions(
    min_value=-1000,
    max_value=1000,
    max_denominator=1000,
)

data_lists = st.lists(
    finite_numbers,
    min_size=2,
    max_size=30,
)

@given(data_lists)
def test_statistics_variance_is_non_negative(data):
    assert statistics.variance(data) >= 0

@given(data_lists)
def test_statistics_variance_matches_definition(data):
    mean = statistics.mean(data)
    expected = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    assert statistics.variance(data) == expected

@given(finite_numbers, st.integers(min_value=2, max_value=30))
def test_statistics_variance_is_zero_for_identical_values(value, size):
    data = [value] * size
    assert statistics.variance(data) == 0

@given(data_lists, finite_numbers)
def test_statistics_variance_is_translation_invariant(data, constant):
    shifted = [x + constant for x in data]
    assert statistics.variance(shifted) == statistics.variance(data)

@given(data_lists, finite_numbers)
def test_statistics_variance_scales_quadratically(data, factor):
    scaled = [x * factor for x in data]
    assert statistics.variance(scaled) == statistics.variance(data) * factor ** 2

# End program