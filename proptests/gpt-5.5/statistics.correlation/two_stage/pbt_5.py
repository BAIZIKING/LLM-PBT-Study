from hypothesis import given, strategies as st, assume
import statistics
import math

SAFE_INTS = st.integers(min_value=-1_000, max_value=1_000)


def draw_nonconstant_list(data, length):
    values = data.draw(st.lists(SAFE_INTS, min_size=length, max_size=length))
    assume(any(value != values[0] for value in values))
    return values


def draw_valid_pair(data):
    length = data.draw(st.integers(min_value=2, max_value=50))
    x = draw_nonconstant_list(data, length)
    y = draw_nonconstant_list(data, length)
    return x, y


@given(st.data())
def test_statistics_correlation_result_is_between_minus_one_and_one(data):
    x, y = draw_valid_pair(data)
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    result = statistics.correlation(x, y, method=method)

    assert -1.0 - 1e-12 <= result <= 1.0 + 1e-12


@given(st.data())
def test_statistics_correlation_is_symmetric(data):
    x, y = draw_valid_pair(data)
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    forward = statistics.correlation(x, y, method=method)
    reverse = statistics.correlation(y, x, method=method)

    assert math.isclose(forward, reverse, rel_tol=1e-12, abs_tol=1e-12)


@given(st.data())
def test_statistics_correlation_of_input_with_itself_is_one(data):
    length = data.draw(st.integers(min_value=2, max_value=50))
    x = draw_nonconstant_list(data, length)
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    result = statistics.correlation(x, x, method=method)

    assert math.isclose(result, 1.0, rel_tol=1e-12, abs_tol=1e-12)


@given(st.data())
def test_statistics_linear_correlation_shift_invariant_and_negative_scale_flips_sign(data):
    x, y = draw_valid_pair(data)
    x_shift = data.draw(st.integers(min_value=-1_000, max_value=1_000))
    y_shift = data.draw(st.integers(min_value=-1_000, max_value=1_000))
    negative_scale = data.draw(st.integers(min_value=-10, max_value=-1))

    base = statistics.correlation(x, y)
    shifted = statistics.correlation(
        [value + x_shift for value in x],
        [value + y_shift for value in y],
    )
    negatively_scaled = statistics.correlation(
        x,
        [negative_scale * value for value in y],
    )

    assert math.isclose(base, shifted, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(negatively_scaled, -base, rel_tol=1e-12, abs_tol=1e-12)


@given(st.data())
def test_statistics_ranked_correlation_is_invariant_under_strictly_increasing_transform(data):
    x, y = draw_valid_pair(data)
    x_scale = data.draw(st.integers(min_value=1, max_value=10))
    y_scale = data.draw(st.integers(min_value=1, max_value=10))
    x_offset = data.draw(st.integers(min_value=-1_000, max_value=1_000))
    y_offset = data.draw(st.integers(min_value=-1_000, max_value=1_000))

    base = statistics.correlation(x, y, method="ranked")
    transformed = statistics.correlation(
        [x_scale * value + x_offset for value in x],
        [y_scale * value + y_offset for value in y],
        method="ranked",
    )

    assert math.isclose(base, transformed, rel_tol=1e-12, abs_tol=1e-12)


# End program