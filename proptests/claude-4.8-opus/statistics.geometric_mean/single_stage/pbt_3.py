from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists drawn from positive floats/ints (valid case) plus
# occasionally inject zeros, negatives, or produce empty lists to exercise
# the StatisticsError paths. Check error conditions per the docs, and for
# valid all-positive input verify the result is positive and bounded between
# the min and max of the data.
@given(st.data())
def test_statistics_geometric_mean(data):
    # Strategy for individual valid positive values (ints or floats)
    positive_value = st.one_of(
        st.integers(min_value=1, max_value=10**6),
        st.floats(min_value=1e-6, max_value=1e6,
                  allow_nan=False, allow_infinity=False),
    )
    # Strategy for "bad" values that should trigger StatisticsError
    bad_value = st.one_of(
        st.just(0),
        st.just(0.0),
        st.integers(min_value=-10**6, max_value=-1),
        st.floats(min_value=-1e6, max_value=-1e-6,
                  allow_nan=False, allow_infinity=False),
    )

    # Draw a base list; allow empty and allow injection of bad values.
    values = data.draw(
        st.lists(st.one_of(positive_value, bad_value), min_size=0, max_size=20)
    )

    # Determine whether this input should raise an error.
    is_empty = len(values) == 0
    has_nonpositive = any(float(v) <= 0 for v in values)

    if is_empty or has_nonpositive:
        try:
            statistics.geometric_mean(values)
            assert False, (
                f"Expected StatisticsError for input {values!r} "
                f"(empty={is_empty}, has_nonpositive={has_nonpositive})"
            )
        except statistics.StatisticsError:
            pass
    else:
        result = statistics.geometric_mean(values)

        # Property: result is a positive float.
        assert isinstance(result, float)
        assert result > 0, f"Geometric mean should be positive, got {result}"

        floats = [float(v) for v in values]
        lo, hi = min(floats), max(floats)

        # Property: single element -> geometric mean equals that element.
        if len(floats) == 1:
            assert math.isclose(result, floats[0], rel_tol=1e-9, abs_tol=1e-9)

        # Property: geometric mean is bounded by min and max of the data
        # (allowing for floating-point error).
        tol = 1e-6 * max(1.0, hi)
        assert lo - tol <= result <= hi + tol, (
            f"Geometric mean {result} not in [{lo}, {hi}] for {values!r}"
        )
# End program