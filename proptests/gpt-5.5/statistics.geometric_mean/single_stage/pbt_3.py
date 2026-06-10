from hypothesis import given, strategies as st
import math
import statistics
from statistics import StatisticsError

# Summary: Generate empty and non-empty list/tuple/generator inputs containing finite ints/floats, with many edge cases such as negatives, -0.0, 0.0, tiny positives, ordinary positives, and very large positives. Check that empty/zero/negative data raises StatisticsError, and otherwise that the result is a float close to exp(mean(log(float(x)))).
@given(st.data())
def test_statistics_geometric_mean(data):
    number_strategy = st.one_of(
        st.integers(min_value=-10**12, max_value=10**12),
        st.floats(
            min_value=-1e100,
            max_value=1e100,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        ),
        st.sampled_from([
            -1.0,
            -0.0,
            0.0,
            1.0,
            2.0,
            10.0,
            1e-300,
            1e-100,
            1e100,
        ]),
    )

    values = data.draw(st.lists(number_strategy, min_size=0, max_size=40))
    container_kind = data.draw(st.sampled_from(["list", "tuple", "generator"]))

    converted = [float(x) for x in values]

    if container_kind == "list":
        input_data = list(values)
    elif container_kind == "tuple":
        input_data = tuple(values)
    else:
        input_data = (x for x in values)

    should_raise = len(converted) == 0 or any(x <= 0.0 for x in converted)

    if should_raise:
        try:
            statistics.geometric_mean(input_data)
        except StatisticsError:
            pass
        else:
            assert False, "Expected StatisticsError for empty, zero, or negative input"
    else:
        result = statistics.geometric_mean(input_data)
        expected = math.exp(math.fsum(math.log(x) for x in converted) / len(converted))

        assert isinstance(result, float)
        assert result > 0.0
        assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=0.0)

# End program