from hypothesis import given, strategies as st
import statistics
import math

# Summary: Generate lists (min size 2) of bounded finite floats to test variance.
# We check non-negativity, zero-variance for constant data, consistency of the
# xbar argument with auto-computed mean, agreement with the manual N-1 formula,
# and translation invariance (shifting all values by a constant).
@given(st.data())
def test_statistics_variance(data):
    values = data.draw(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6,
                      allow_nan=False, allow_infinity=False),
            min_size=2, max_size=50,
        )
    )

    result = statistics.variance(values)
    n = len(values)
    mean = sum(values) / n

    # Property 1: Variance is non-negative.
    assert result >= -1e-9, f"Variance should be non-negative, got {result}"

    # Property 2: Constant data has zero variance.
    if all(v == values[0] for v in values):
        assert math.isclose(result, 0.0, abs_tol=1e-9), \
            f"Constant data should have variance 0, got {result}"

    # Property 3: Passing the actual mean as xbar gives the same result.
    result_with_xbar = statistics.variance(values, mean)
    assert math.isclose(result, result_with_xbar, rel_tol=1e-9, abs_tol=1e-9), \
        f"Variance with xbar ({result_with_xbar}) should match auto ({result})"

    # Property 4: Matches the manual N-1 (Bessel's correction) formula.
    expected = sum((x - mean) ** 2 for x in values) / (n - 1)
    assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-6), \
        f"Variance {result} should match manual formula {expected}"

    # Property 5: Translation invariance (shift all values by a constant).
    shift = 123.456
    shifted = [v + shift for v in values]
    result_shifted = statistics.variance(shifted)
    assert math.isclose(result, result_shifted, rel_tol=1e-6, abs_tol=1e-6), \
        f"Variance should be translation invariant: {result} vs {result_shifted}"
# End program