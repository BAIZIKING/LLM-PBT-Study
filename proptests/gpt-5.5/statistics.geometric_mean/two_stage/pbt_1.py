from hypothesis import given, strategies as st
import statistics
import math
import pytest

positive_floats = st.floats(
    min_value=1e-200,
    max_value=1e200,
    allow_nan=False,
    allow_infinity=False,
)

positive_float_lists = st.lists(
    positive_floats,
    min_size=1,
    max_size=100,
)

invalid_float_lists = st.one_of(
    st.just([]),
    st.lists(positive_floats, min_size=0, max_size=50).flatmap(
        lambda xs: st.tuples(
            st.just(xs),
            st.floats(
                min_value=-1e200,
                max_value=0.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            st.lists(positive_floats, min_size=0, max_size=50),
        ).map(lambda t: t[0] + [t[1]] + t[2])
    ),
)

@given(positive_float_lists)
def test_statistics_geometric_mean_result_is_finite_positive_float(data):
    result = statistics.geometric_mean(data)

    assert isinstance(result, float)
    assert math.isfinite(result)
    assert result > 0.0

@given(positive_floats)
def test_statistics_geometric_mean_singleton_equals_float_value(x):
    result = statistics.geometric_mean([x])

    assert math.isclose(result, float(x), rel_tol=1e-12, abs_tol=0.0)

@given(positive_float_lists)
def test_statistics_geometric_mean_lies_between_minimum_and_maximum(data):
    result = statistics.geometric_mean(data)

    minimum = min(data)
    maximum = max(data)

    assert result >= minimum or math.isclose(result, minimum, rel_tol=1e-12, abs_tol=0.0)
    assert result <= maximum or math.isclose(result, maximum, rel_tol=1e-12, abs_tol=0.0)

@given(positive_float_lists)
def test_statistics_geometric_mean_is_order_independent(data):
    result = statistics.geometric_mean(data)
    reversed_result = statistics.geometric_mean(list(reversed(data)))

    assert math.isclose(result, reversed_result, rel_tol=1e-12, abs_tol=0.0)

@given(invalid_float_lists)
def test_statistics_geometric_mean_rejects_empty_zero_or_negative_data(data):
    with pytest.raises(statistics.StatisticsError):
        statistics.geometric_mean(data)
# End program