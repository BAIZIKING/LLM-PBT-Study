from hypothesis import given, strategies as st
import statistics
from fractions import Fraction
from decimal import Decimal
import math
import pytest

# Summary: Generate non-empty lists of one consistent numeric type (int, finite float,
# Fraction, or Decimal) covering negatives, zeros, large magnitudes and single elements.
# Verify mean == sum/len, that min <= mean <= max, single-element identity, and that
# empty input raises StatisticsError.
@given(st.data())
def test_statistics_mean(data):
    int_strat = st.lists(st.integers(min_value=-10**9, max_value=10**9), min_size=1)
    float_strat = st.lists(
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e9, max_value=1e9),
        min_size=1,
    )
    frac_strat = st.lists(
        st.builds(Fraction,
                  st.integers(min_value=-1000, max_value=1000),
                  st.integers(min_value=1, max_value=1000)),
        min_size=1,
    )
    dec_strat = st.lists(
        st.decimals(allow_nan=False, allow_infinity=False,
                    min_value=Decimal("-1e6"), max_value=Decimal("1e6"),
                    places=4),
        min_size=1,
    )

    values = data.draw(st.one_of(int_strat, float_strat, frac_strat, dec_strat))

    result = statistics.mean(values)

    # Property 1: definition -> mean == sum / len
    expected = sum(values) / len(values)
    if any(isinstance(v, float) for v in values):
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)
    else:
        # exact types (int, Fraction, Decimal)
        assert result == expected

    # Property 2: central location -> min <= mean <= max
    lo, hi = min(values), max(values)
    if any(isinstance(v, float) for v in values):
        tol = 1e-9 + 1e-9 * max(abs(lo), abs(hi))
        assert lo - tol <= result <= hi + tol
    else:
        assert lo <= result <= hi

    # Property 3: single-element identity
    if len(values) == 1:
        assert result == values[0]

    # Property 4: empty input raises StatisticsError
    with pytest.raises(statistics.StatisticsError):
        statistics.mean([])
# End program