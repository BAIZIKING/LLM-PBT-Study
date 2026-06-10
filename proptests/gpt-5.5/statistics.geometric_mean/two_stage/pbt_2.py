from hypothesis import given, strategies as st
import statistics
import math

POSITIVE_FLOATS = st.floats(
    min_value=1e-100,
    max_value=1e100,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

POSITIVE_LISTS = st.lists(
    POSITIVE_FLOATS,
    min_size=1,
    max_size=50,
)


@given(st.data())
def test_statistics_geometric_mean_returns_positive_float(data):
    values = data.draw(POSITIVE_LISTS)

    result = statistics.geometric_mean(values)

    assert isinstance(result, float)
    assert math.isfinite(result)
    assert result > 0.0


@given(st.data())
def test_statistics_geometric_mean_lies_between_minimum_and_maximum(data):
    values = data.draw(POSITIVE_LISTS)

    result = statistics.geometric_mean(values)
    minimum = min(values)
    maximum = max(values)

    assert result >= minimum or math.isclose(
        result, minimum, rel_tol=1e-12, abs_tol=1e-300
    )
    assert result <= maximum or math.isclose(
        result, maximum, rel_tol=1e-12, abs_tol=1e-300
    )


@given(st.data())
def test_statistics_geometric_mean_is_invariant_under_reordering(data):
    values = data.draw(POSITIVE_LISTS)

    result_original = statistics.geometric_mean(values)
    result_reordered = statistics.geometric_mean(list(reversed(values)))

    assert math.isclose(
        result_original,
        result_reordered,
        rel_tol=1e-12,
        abs_tol=1e-300,
    )


@given(st.data())
def test_statistics_geometric_mean_scales_with_positive_constant(data):
    values = data.draw(
        st.lists(
            st.floats(
                min_value=1e-50,
                max_value=1e50,
                allow_nan=False,
                allow_infinity=False,
                width=64,
            ),
            min_size=1,
            max_size=50,
        )
    )
    scale = data.draw(
        st.floats(
            min_value=1e-50,
            max_value=1e50,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )
    )

    original_result = statistics.geometric_mean(values)
    scaled_result = statistics.geometric_mean([x * scale for x in values])

    assert math.isclose(
        scaled_result,
        original_result * scale,
        rel_tol=1e-11,
        abs_tol=1e-300,
    )


@given(st.data())
def test_statistics_geometric_mean_rejects_empty_zero_or_negative_input(data):
    non_positive_float = st.floats(
        min_value=-1e100,
        max_value=0.0,
        allow_nan=False,
        allow_infinity=False,
        width=64,
    )

    invalid_values = data.draw(
        st.one_of(
            st.just([]),
            st.tuples(
                st.lists(POSITIVE_FLOATS, max_size=25),
                non_positive_float,
                st.lists(POSITIVE_FLOATS, max_size=25),
            ).map(lambda parts: parts[0] + [parts[1]] + parts[2]),
        )
    )

    try:
        statistics.geometric_mean(invalid_values)
    except statistics.StatisticsError:
        pass
    else:
        assert False


# End program