from hypothesis import given, strategies as st
import math
import statistics
from decimal import Decimal, localcontext
from fractions import Fraction

# Summary: Draw empty and non-empty homogeneous numeric data from several supported families
# (bounded ints, finite floats, Fractions, and finite Decimals), including negatives, zeros,
# duplicates, and singletons. Present the same values as a list, tuple, or one-shot iterator
# to exercise both sequence and iterable inputs. Check that empty data raises StatisticsError;
# otherwise check that the result is the arithmetic mean, is within the input range, and that
# singleton data returns the sole value.
@given(st.data())
def test_statistics_mean(data):
    numeric_kind = data.draw(st.sampled_from(["int", "float", "fraction", "decimal"]))

    if numeric_kind == "int":
        element_strategy = st.integers(min_value=-1_000_000, max_value=1_000_000)
    elif numeric_kind == "float":
        element_strategy = st.floats(
            min_value=-1_000_000,
            max_value=1_000_000,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        )
    elif numeric_kind == "fraction":
        element_strategy = st.fractions(
            min_value=Fraction(-1_000_000, 1),
            max_value=Fraction(1_000_000, 1),
            max_denominator=1000,
        )
    else:
        element_strategy = st.decimals(
            min_value=Decimal("-1000000"),
            max_value=Decimal("1000000"),
            allow_nan=False,
            allow_infinity=False,
            places=4,
        )

    values = data.draw(st.lists(element_strategy, min_size=0, max_size=30))
    container_kind = data.draw(st.sampled_from(["list", "tuple", "iterator"]))

    if container_kind == "list":
        mean_input = list(values)
    elif container_kind == "tuple":
        mean_input = tuple(values)
    else:
        mean_input = iter(values)

    if not values:
        try:
            statistics.mean(mean_input)
        except statistics.StatisticsError:
            return
        assert False, "statistics.mean() must raise StatisticsError for empty data"

    with localcontext() as ctx:
        ctx.prec = 50
        result = statistics.mean(mean_input)

        if numeric_kind == "float":
            expected = math.fsum(values) / len(values)
            assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)
        elif numeric_kind == "fraction":
            expected = sum(values, Fraction(0, 1)) / len(values)
            assert result == expected
        elif numeric_kind == "decimal":
            expected = sum(values, Decimal(0)) / Decimal(len(values))
            assert result == expected
        else:
            expected = sum(values) / len(values)
            assert result == expected

    assert min(values) <= result <= max(values)

    if len(values) == 1:
        assert result == values[0]
# End program