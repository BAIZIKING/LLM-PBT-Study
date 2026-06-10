from hypothesis import given, strategies as st
import statistics
import math

def non_constant_int_list(length):
    return st.lists(
        st.integers(min_value=-10_000, max_value=10_000),
        min_size=length,
        max_size=length,
    ).filter(lambda xs: len(set(xs)) > 1)

@given(st.data())
def test_statistics_correlation_result_is_bounded(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(non_constant_int_list(n))
    y = data.draw(non_constant_int_list(n))
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    result = statistics.correlation(x, y, method=method)

    assert math.isfinite(result)
    assert -1.0 - 1e-12 <= result <= 1.0 + 1e-12

@given(st.data())
def test_statistics_correlation_is_symmetric(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(non_constant_int_list(n))
    y = data.draw(non_constant_int_list(n))
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    result_xy = statistics.correlation(x, y, method=method)
    result_yx = statistics.correlation(y, x, method=method)

    assert math.isclose(result_xy, result_yx, rel_tol=1e-12, abs_tol=1e-12)

@given(st.data())
def test_statistics_correlation_of_input_with_itself_is_one(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(non_constant_int_list(n))
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    result = statistics.correlation(x, x, method=method)

    assert math.isclose(result, 1.0, rel_tol=1e-12, abs_tol=1e-12)

@given(st.data())
def test_statistics_correlation_linear_affine_transformation(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(non_constant_int_list(n))
    y = data.draw(non_constant_int_list(n))
    scale = data.draw(
        st.integers(min_value=-20, max_value=20).filter(lambda value: value != 0)
    )
    offset = data.draw(st.integers(min_value=-10_000, max_value=10_000))

    transformed_x = [scale * value + offset for value in x]

    original = statistics.correlation(x, y, method="linear")
    transformed = statistics.correlation(transformed_x, y, method="linear")
    expected = original if scale > 0 else -original

    assert math.isclose(transformed, expected, rel_tol=1e-12, abs_tol=1e-12)

@given(st.data())
def test_statistics_correlation_ranked_same_and_opposite_ordering(data):
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.permutations(range(n)))

    same_order = [3 * value + 7 for value in x]
    opposite_order = [-value for value in x]

    same_result = statistics.correlation(x, same_order, method="ranked")
    opposite_result = statistics.correlation(x, opposite_order, method="ranked")

    assert math.isclose(same_result, 1.0, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(opposite_result, -1.0, rel_tol=1e-12, abs_tol=1e-12)
# End program