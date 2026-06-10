from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists of floats/ints that may be empty, or contain positive,
# zero, or negative values to exercise both valid computation paths and the
# documented error conditions (empty, zero, or negative input).
@given(st.data())
def test_statistics_geometric_mean(data):
    # Strategy: numbers that can be positive, zero, or negative, in a safe range.
    element_strategy = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False
    )
    values = data.draw(st.lists(element_strategy, min_size=0, max_size=20))

    is_empty = len(values) == 0
    has_nonpositive = any(v <= 0 for v in values)

    if is_empty or has_nonpositive:
        # Property 1: empty, zero, or negative input must raise StatisticsError.
        try:
            statistics.geometric_mean(values)
            assert False, "Expected StatisticsError for empty/zero/negative input"
        except statistics.StatisticsError:
            pass
    else:
        # All values are strictly positive here.
        result = statistics.geometric_mean(values)

        # Property 3: geometric mean of positive values is positive.
        assert result > 0

        lo = min(values)
        hi = max(values)
        tol = 1e-6 * max(1.0, hi)

        # Property 2: min <= geometric_mean <= max (within float tolerance).
        assert lo - tol <= result <= hi + tol

        # Property 4: AM-GM inequality: geometric mean <= arithmetic mean.
        arithmetic_mean = statistics.fmean(values)
        assert result <= arithmetic_mean + tol
# End program