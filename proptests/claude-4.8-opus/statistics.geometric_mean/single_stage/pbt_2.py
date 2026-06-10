from hypothesis import given, strategies as st
import math
import statistics
import pytest

# Summary: Generate lists that are either all-positive (valid), or contain
# edge cases (empty, zero, or negative values) which should raise StatisticsError.
# For valid inputs, verify the geometric mean equals exp(mean(log(x))), lies
# within [min, max], and equals the element itself for single-element lists.
@given(st.data())
def test_statistics_geometric_mean(data):
    # Strategy for valid positive numbers
    positive_numbers = st.floats(
        min_value=1e-3, max_value=1e6,
        allow_nan=False, allow_infinity=False
    )
    valid_lists = st.lists(positive_numbers, min_size=1, max_size=20)

    # Strategy for invalid lists: empty, or containing zero/negative
    nonpositive_numbers = st.floats(
        min_value=-1e6, max_value=0.0,
        allow_nan=False, allow_infinity=False
    )
    any_numbers = st.one_of(positive_numbers, nonpositive_numbers)
    invalid_lists = st.one_of(
        st.just([]),  # empty
        st.lists(any_numbers, min_size=1, max_size=20).filter(
            lambda xs: any(x <= 0 for x in xs)
        ),
    )

    sample = data.draw(st.one_of(valid_lists, invalid_lists))

    # Determine whether this input should error per the documentation
    should_error = (len(sample) == 0) or any(x <= 0 for x in sample)

    if should_error:
        with pytest.raises(statistics.StatisticsError):
            statistics.geometric_mean(sample)
    else:
        result = statistics.geometric_mean(sample)

        # Result must be a positive float
        assert result > 0

        # Property: geometric mean lies within [min, max] (allowing tolerance)
        lo, hi = min(sample), max(sample)
        assert lo <= result + 1e-6
        assert result <= hi + 1e-6

        # Property: matches exp(mean(log(x))) computed independently
        expected = math.exp(math.fsum(math.log(x) for x in sample) / len(sample))
        assert math.isclose(result, expected, rel_tol=1e-6, abs_tol=1e-9)

        # Property: single-element list returns that element
        if len(sample) == 1:
            assert math.isclose(result, sample[0], rel_tol=1e-6, abs_tol=1e-9)
# End program