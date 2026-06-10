from hypothesis import given, strategies as st
from statistics import StatisticsError, correlation
import math

# Summary: Generate valid and invalid x/y pairs with both supported methods ("linear" and
# "ranked"). The strategy covers too-short inputs, mismatched lengths, constant inputs,
# arbitrary non-constant numeric inputs, exact linear transforms, and monotonic nonlinear
# transforms. The test checks documented error cases, coefficient bounds [-1, 1], perfect
# positive/negative relationships, and that "ranked" correlation equals Pearson correlation
# over averaged ranks.
@given(st.data())
def test_statistics_correlation(data):
    method = data.draw(st.sampled_from(["linear", "ranked"]))

    number = st.one_of(
        st.integers(min_value=-10_000, max_value=10_000),
        st.floats(
            min_value=-1_000_000,
            max_value=1_000_000,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=False,
            width=32,
        ),
    )

    def expect_statistics_error(x, y):
        try:
            correlation(x, y, method=method)
        except StatisticsError:
            return
        assert False, "Expected StatisticsError"

    def draw_nonconstant_list(size):
        first = data.draw(number)
        second = data.draw(number.filter(lambda v: v != first))
        rest = data.draw(st.lists(number, min_size=size - 2, max_size=size - 2))
        return [first, second] + rest

    def averaged_ranks(values):
        order = sorted(range(len(values)), key=values.__getitem__)
        ranks = [0.0] * len(values)

        i = 0
        while i < len(values):
            j = i + 1
            while j < len(values) and values[order[j]] == values[order[i]]:
                j += 1

            # Average of one-based ranks i+1 through j.
            avg_rank = (i + 1 + j) / 2.0
            for k in range(i, j):
                ranks[order[k]] = avg_rank

            i = j

        return ranks

    scenario = data.draw(
        st.sampled_from(
            [
                "too_short",
                "mismatched_lengths",
                "constant_input",
                "arbitrary_valid",
                "perfect_linear_transform",
                "monotonic_nonlinear_transform",
            ]
        )
    )

    if scenario == "too_short":
        n = data.draw(st.integers(min_value=0, max_value=1))
        x = data.draw(st.lists(number, min_size=n, max_size=n))
        y = data.draw(st.lists(number, min_size=n, max_size=n))
        expect_statistics_error(x, y)

    elif scenario == "mismatched_lengths":
        n = data.draw(st.integers(min_value=0, max_value=20))
        m = data.draw(st.integers(min_value=0, max_value=20).filter(lambda v: v != n))
        x = data.draw(st.lists(number, min_size=n, max_size=n))
        y = data.draw(st.lists(number, min_size=m, max_size=m))
        expect_statistics_error(x, y)

    elif scenario == "constant_input":
        n = data.draw(st.integers(min_value=2, max_value=20))
        constant_value = data.draw(number)
        other = draw_nonconstant_list(n)

        if data.draw(st.booleans()):
            x = [constant_value] * n
            y = other
        else:
            x = other
            y = [constant_value] * n

        expect_statistics_error(x, y)

    elif scenario == "arbitrary_valid":
        n = data.draw(st.integers(min_value=2, max_value=20))
        x = draw_nonconstant_list(n)
        y = draw_nonconstant_list(n)

        result = correlation(x, y, method=method)

        assert math.isfinite(result)
        assert -1.000000000001 <= result <= 1.000000000001

        if method == "ranked":
            expected = correlation(averaged_ranks(x), averaged_ranks(y), method="linear")
            assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)

    elif scenario == "perfect_linear_transform":
        n = data.draw(st.integers(min_value=2, max_value=20))
        first = data.draw(st.integers(min_value=-1_000, max_value=1_000))
        second = data.draw(
            st.integers(min_value=-1_000, max_value=1_000).filter(lambda v: v != first)
        )
        rest = data.draw(
            st.lists(st.integers(min_value=-1_000, max_value=1_000), min_size=n - 2, max_size=n - 2)
        )
        x = [first, second] + rest

        slope = data.draw(st.integers(min_value=-20, max_value=20).filter(lambda v: v != 0))
        intercept = data.draw(st.integers(min_value=-1_000, max_value=1_000))
        y = [slope * value + intercept for value in x]

        result = correlation(x, y, method=method)
        expected = 1.0 if slope > 0 else -1.0

        assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)

    else:
        n = data.draw(st.integers(min_value=2, max_value=20))
        first = data.draw(st.integers(min_value=-100, max_value=100))
        second = data.draw(
            st.integers(min_value=-100, max_value=100).filter(lambda v: v != first)
        )
        rest = data.draw(
            st.lists(st.integers(min_value=-100, max_value=100), min_size=n - 2, max_size=n - 2)
        )
        x = [first, second] + rest

        direction = data.draw(st.sampled_from([1, -1]))
        y = [direction * (value ** 3) for value in x]

        result = correlation(x, y, method=method)

        assert math.isfinite(result)
        assert -1.000000000001 <= result <= 1.000000000001

        if method == "ranked":
            expected = 1.0 if direction > 0 else -1.0
            assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)

# End program