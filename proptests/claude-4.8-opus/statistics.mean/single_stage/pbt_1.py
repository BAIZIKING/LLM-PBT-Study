from hypothesis import given, strategies as st
from fractions import Fraction
from decimal import Decimal
import statistics
import pytest

# Summary: Generate non-empty lists of one numeric type chosen among ints,
# finite floats, Fractions, and Decimals (covering single elements, identical
# values, negatives, zeros). Verify the mean lies within [min, max], satisfies
# mean*n == sum, equals the constant when all values are equal, and that an
# empty input raises StatisticsError.
@given(st.data())
def test_statistics_mean(data):
    numeric_strategy = data.draw(st.sampled_from([
        st.integers(min_value=-10**6, max_value=10**6),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e9, max_value=1e9),
        st.fractions(),
        st.decimals(allow_nan=False, allow_infinity=False,
                    min_value=Decimal("-1e6"), max_value=Decimal("1e6")),
    ]))
    values = data.draw(st.lists(numeric_strategy, min_size=1, max_size=20))

    result = statistics.mean(values)

    # Property 1: mean lies within [min, max]
    assert min(values) <= result <= max(values)

    # Property 2: mean * n == sum (definition of arithmetic mean)
    # Compare using cross-multiplication to avoid float division issues.
    n = len(values)
    total = sum(values)
    if isinstance(result, float) or any(isinstance(v, float) for v in values):
        assert result * n == pytest.approx(float(total), rel=1e-9, abs=1e-6)
    else:
        assert result * n == total

    # Property 3: if all values are equal, mean equals that value
    if all(v == values[0] for v in values):
        assert result == values[0]

    # Property 4: empty input raises StatisticsError
    with pytest.raises(statistics.StatisticsError):
        statistics.mean([])
# End program