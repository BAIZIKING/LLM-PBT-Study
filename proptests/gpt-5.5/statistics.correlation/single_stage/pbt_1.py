from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate finite integer x/y inputs as lists or tuples, including valid non-constant pairs,
# affine perfect-correlation pairs, tied values for ranked correlation, too-short inputs, mismatched
# lengths, and constant inputs. Randomly exercise the default method, "linear", and "ranked".
# Check documented properties: invalid inputs raise StatisticsError; valid correlations are finite
# and in [-1, 1]; correlation is symmetric; self-correlation is 1; the default equals "linear";
# "ranked" equals Pearson correlation of average ranks; affine relationships produce +/-1.
@given(st.data())
def test_statistics_correlation(data):
    values = st.integers(min_value=-1000, max_value=1000)
    method_choice = data.draw(st.sampled_from(["default", "linear", "ranked"]))
    case = data.draw(
        st.sampled_from(
            ["valid", "affine", "too_short", "mismatched_lengths", "constant_x", "constant_y"]
        )
    )

    def nonconstant_list(n):
        return st.lists(values, min_size=n, max_size=n).filter(lambda xs: len(set(xs)) > 1)

    def maybe_container(xs):
        container_type = data.draw(st.sampled_from([list, tuple]))
        return container_type(xs)

    def call_correlation(x, y, method):
        if method == "default":
            return statistics.correlation(x, y)
        return statistics.correlation(x, y, method=method)

    def assert_statistics_error(x, y, method):
        try:
            call_correlation(x, y, method)
        except statistics.StatisticsError:
            return
        assert False, "statistics.correlation() should have raised StatisticsError"

    def average_ranks(xs):
        ordered = sorted((value, index) for index, value in enumerate(xs))
        ranks = [None] * len(xs)
        start = 0

        while start < len(ordered):
            end = start + 1
            while end < len(ordered) and ordered[end][0] == ordered[start][0]:
                end += 1

            # Average of the 1-based ranks start + 1 through end.
            average_rank = (start + 1 + end) / 2
            for _, original_index in ordered[start:end]:
                ranks[original_index] = average_rank

            start = end

        return ranks

    if case == "too_short":
        n = data.draw(st.integers(min_value=0, max_value=1))
        x = maybe_container(data.draw(st.lists(values, min_size=n, max_size=n)))
        y = maybe_container(data.draw(st.lists(values, min_size=n, max_size=n)))
        assert_statistics_error(x, y, method_choice)
        return

    if case == "mismatched_lengths":
        n = data.draw(st.integers(min_value=0, max_value=10))
        m = data.draw(st.integers(min_value=0, max_value=10).filter(lambda k: k != n))
        x = maybe_container(data.draw(st.lists(values, min_size=n, max_size=n)))
        y = maybe_container(data.draw(st.lists(values, min_size=m, max_size=m)))
        assert_statistics_error(x, y, method_choice)
        return

    if case == "constant_x":
        n = data.draw(st.integers(min_value=2, max_value=20))
        c = data.draw(values)
        x = maybe_container([c] * n)
        y = maybe_container(data.draw(nonconstant_list(n)))
        assert_statistics_error(x, y, method_choice)
        return

    if case == "constant_y":
        n = data.draw(st.integers(min_value=2, max_value=20))
        c = data.draw(values)
        x = maybe_container(data.draw(nonconstant_list(n)))
        y = maybe_container([c] * n)
        assert_statistics_error(x, y, method_choice)
        return

    n = data.draw(st.integers(min_value=2, max_value=20))
    x_list = data.draw(nonconstant_list(n))

    if case == "affine":
        scale = data.draw(
            st.integers(min_value=-10, max_value=10).filter(lambda a: a != 0)
        )
        offset = data.draw(st.integers(min_value=-1000, max_value=1000))
        y_list = [scale * x + offset for x in x_list]
        expected_affine_correlation = 1.0 if scale > 0 else -1.0
    else:
        y_list = data.draw(nonconstant_list(n))
        expected_affine_correlation = None

    x = maybe_container(x_list)
    y = maybe_container(y_list)

    r = call_correlation(x, y, method_choice)
    assert math.isfinite(r)
    assert -1.0 - 1e-12 <= r <= 1.0 + 1e-12

    reversed_r = call_correlation(y, x, method_choice)
    assert math.isclose(r, reversed_r, rel_tol=1e-12, abs_tol=1e-12)

    self_r = call_correlation(x, x, method_choice)
    assert math.isclose(self_r, 1.0, rel_tol=1e-12, abs_tol=1e-12)

    default_r = statistics.correlation(x, y)
    explicit_linear_r = statistics.correlation(x, y, method="linear")
    assert math.isclose(default_r, explicit_linear_r, rel_tol=1e-12, abs_tol=1e-12)

    actual_method = "linear" if method_choice == "default" else method_choice
    if actual_method == "ranked":
        ranked_reference = statistics.correlation(average_ranks(x), average_ranks(y))
        assert math.isclose(r, ranked_reference, rel_tol=1e-12, abs_tol=1e-12)

    if expected_affine_correlation is not None:
        assert math.isclose(
            r,
            expected_affine_correlation,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )

# End program