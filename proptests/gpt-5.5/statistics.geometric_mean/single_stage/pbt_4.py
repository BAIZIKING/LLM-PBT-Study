from hypothesis import given, strategies as st
import math
import statistics
from statistics import StatisticsError

# Summary: Generate empty datasets, valid non-empty positive numeric datasets, and invalid
# datasets containing zero or negative values. Values include ints and finite floats across
# a broad range, including very small positive floats. Each dataset is randomly wrapped as
# a list, tuple, iterator, or generator to cover both sequences and general iterables.
# Properties checked: empty input raises StatisticsError; any zero or negative value raises
# StatisticsError; otherwise the result is a positive finite float close to exp(mean(log(x))).
@given(st.data())
def test_statistics_geometric_mean(data):
    positive_value = st.one_of(
        st.integers(min_value=1, max_value=10**12),
        st.floats(
            min_value=0.0,
            max_value=1e100,
            exclude_min=True,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=True,
        ),
    )

    negative_value = st.one_of(
        st.integers(min_value=-(10**12), max_value=-1),
        st.floats(
            min_value=-1e100,
            max_value=0.0,
            exclude_max=True,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=True,
        ),
    )

    zero_value = st.sampled_from([0, 0.0, -0.0])

    case = data.draw(st.sampled_from(["empty", "valid_positive", "contains_zero", "contains_negative"]))

    if case == "empty":
        values = []
        should_raise = True
    elif case == "valid_positive":
        values = data.draw(st.lists(positive_value, min_size=1, max_size=25))
        should_raise = False
    else:
        bad_value = data.draw(zero_value if case == "contains_zero" else negative_value)
        prefix = data.draw(st.lists(positive_value, max_size=10))
        suffix = data.draw(st.lists(positive_value, max_size=10))
        values = prefix + [bad_value] + suffix
        should_raise = True

    wrapper = data.draw(st.sampled_from(["list", "tuple", "iterator", "generator"]))

    if wrapper == "list":
        dataset = list(values)
    elif wrapper == "tuple":
        dataset = tuple(values)
    elif wrapper == "iterator":
        dataset = iter(values)
    else:
        dataset = (x for x in values)

    if should_raise:
        try:
            statistics.geometric_mean(dataset)
        except StatisticsError:
            pass
        else:
            assert False, "Expected StatisticsError for empty data or data containing zero/negative values"
    else:
        result = statistics.geometric_mean(dataset)
        expected = math.exp(math.fsum(math.log(float(x)) for x in values) / len(values))

        assert isinstance(result, float)
        assert math.isfinite(result)
        assert result > 0.0
        assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=0.0)
# End program