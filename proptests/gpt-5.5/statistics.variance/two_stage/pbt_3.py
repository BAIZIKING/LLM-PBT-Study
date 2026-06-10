from hypothesis import given, strategies as st
import statistics
from fractions import Fraction

MAX_ABS_VALUE = 10**6
MAX_ABS_SCALE = 10**3
MAX_SIZE = 50

fraction_values = st.integers(
    min_value=-MAX_ABS_VALUE,
    max_value=MAX_ABS_VALUE,
).map(Fraction)

sample_data = st.lists(
    fraction_values,
    min_size=2,
    max_size=MAX_SIZE,
)


@given(st.data())
def test_statistics_variance_is_non_negative(data):
    values = data.draw(sample_data)

    result = statistics.variance(values)

    assert result >= 0


@given(st.data())
def test_statistics_variance_is_zero_iff_all_values_are_equal(data):
    values = data.draw(sample_data)

    result = statistics.variance(values)
    all_values_are_equal = all(value == values[0] for value in values)

    assert (result == 0) == all_values_are_equal


@given(st.data())
def test_statistics_variance_matches_sample_variance_formula(data):
    values = data.draw(sample_data)

    mean = statistics.mean(values)
    expected = sum((value - mean) ** 2 for value in values) / (len(values) - 1)

    assert statistics.variance(values) == expected


@given(st.data())
def test_statistics_variance_with_actual_xbar_matches_default(data):
    values = data.draw(sample_data)

    mean = statistics.mean(values)

    assert statistics.variance(values, mean) == statistics.variance(values)
    assert statistics.variance(values, None) == statistics.variance(values)


@given(st.data())
def test_statistics_variance_translation_and_scaling(data):
    values = data.draw(sample_data)
    offset = data.draw(
        st.integers(min_value=-MAX_ABS_VALUE, max_value=MAX_ABS_VALUE).map(Fraction)
    )
    scale = data.draw(
        st.integers(min_value=-MAX_ABS_SCALE, max_value=MAX_ABS_SCALE).map(Fraction)
    )

    original_variance = statistics.variance(values)

    translated_values = [value + offset for value in values]
    scaled_values = [value * scale for value in values]

    assert statistics.variance(translated_values) == original_variance
    assert statistics.variance(scaled_values) == original_variance * scale**2


# End program