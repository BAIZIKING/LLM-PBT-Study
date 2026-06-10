from hypothesis import given, strategies as st
import math
from decimal import Decimal
from fractions import Fraction
from statistics import StatisticsError, mean, pvariance, variance as statistics_variance

# Summary: Generate homogeneous numeric iterables as lists, tuples, or fresh iterators containing ints, finite floats, Decimals, or Fractions, including empty/singleton inputs, negatives, zeros, repeated values, and all-equal sequences. Check that inputs with fewer than two values raise StatisticsError; otherwise, omitted xbar, xbar=None, and xbar=mean(data) agree, the result is non-negative, all-equal data has zero variance, and sample variance matches pvariance(data) * n / (n - 1). Arbitrary xbar values are not asserted because the documentation warns they can produce invalid results.
@given(st.data())
def test_statistics_variance(data):
    numeric_kind = data.draw(st.sampled_from(["int", "float", "decimal", "fraction"]))

    if numeric_kind == "int":
        element_strategy = st.integers(min_value=-(10**12), max_value=10**12)
    elif numeric_kind == "float":
        element_strategy = st.one_of(
            st.just(0.0),
            st.just(-0.0),
            st.floats(
                min_value=-1e50,
                max_value=1e50,
                allow_nan=False,
                allow_infinity=False,
                width=64,
            ),
        )
    elif numeric_kind == "decimal":
        element_strategy = st.decimals(
            min_value=Decimal("-1000000000000"),
            max_value=Decimal("1000000000000"),
            allow_nan=False,
            allow_infinity=False,
            places=6,
        )
    else:
        element_strategy = st.fractions(
            min_value=Fraction(-10**6),
            max_value=Fraction(10**6),
            max_denominator=1000,
        )

    values = data.draw(
        st.one_of(
            st.lists(element_strategy, min_size=0, max_size=30),
            element_strategy.flatmap(
                lambda x: st.lists(st.just(x), min_size=0, max_size=30)
            ),
        )
    )

    container_kind = data.draw(st.sampled_from(["list", "tuple", "iterator"]))

    def fresh_iterable():
        if container_kind == "list":
            return list(values)
        if container_kind == "tuple":
            return tuple(values)
        return iter(values)

    def close_enough(a, b):
        if a == b:
            return True
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)

    if len(values) < 2:
        for call in (
            lambda: statistics_variance(fresh_iterable()),
            lambda: statistics_variance(fresh_iterable(), None),
            lambda: statistics_variance(fresh_iterable(), 0),
        ):
            try:
                call()
            except StatisticsError:
                pass
            else:
                assert False, "variance() must raise StatisticsError for fewer than two values"
        return

    baseline = statistics_variance(fresh_iterable())
    none_xbar_result = statistics_variance(fresh_iterable(), None)
    mean_value = mean(fresh_iterable())
    correct_xbar_result = statistics_variance(fresh_iterable(), mean_value)

    xbar_mode = data.draw(st.sampled_from(["omitted", "none", "correct_mean"]))
    if xbar_mode == "omitted":
        selected_result = statistics_variance(fresh_iterable())
    elif xbar_mode == "none":
        selected_result = statistics_variance(fresh_iterable(), None)
    else:
        selected_result = statistics_variance(fresh_iterable(), mean_value)

    assert close_enough(none_xbar_result, baseline)
    assert close_enough(correct_xbar_result, baseline)
    assert close_enough(selected_result, baseline)

    assert baseline >= 0

    if all(x == values[0] for x in values):
        assert baseline == 0

    expected_from_population_variance = pvariance(fresh_iterable()) * len(values) / (len(values) - 1)
    assert close_enough(baseline, expected_from_population_variance)
# End program