from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists of >=2 finite, bounded floats to keep mathematical
# properties (non-negativity, translation invariance, scaling) numerically
# stable, while a separate strategy produces all-identical lists for the
# zero-variance edge case. Verify non-negativity, zero-variance for constant
# data, equivalence of passing xbar, translation invariance, and the k^2
# scaling law.
@given(st.data())
def test_statistics_variance(data):
    finite_floats = st.floats(
        min_value=-1e6, max_value=1e6,
        allow_nan=False, allow_infinity=False
    )
    values = data.draw(st.lists(finite_floats, min_size=2, max_size=50))

    v = statistics.variance(values)

    # Property 1: variance is non-negative (allow tiny FP error)
    assert v >= -1e-6

    # Property 2: zero variance when all values identical
    const = data.draw(finite_floats)
    n = data.draw(st.integers(min_value=2, max_value=50))
    const_list = [const] * n
    assert math.isclose(statistics.variance(const_list), 0.0, abs_tol=1e-9)

    # Property 3: passing precomputed mean as xbar gives same result
    m = statistics.mean(values)
    v_with_xbar = statistics.variance(values, m)
    assert math.isclose(v, v_with_xbar, rel_tol=1e-9, abs_tol=1e-9)

    # Property 4: translation invariance (shift by constant c)
    c = data.draw(finite_floats)
    shifted = [x + c for x in values]
    v_shifted = statistics.variance(shifted)
    scale = max(1.0, abs(v))
    assert math.isclose(v, v_shifted, rel_tol=1e-6, abs_tol=1e-6 * scale)

    # Property 5: scaling by k multiplies variance by k^2
    k = data.draw(st.floats(min_value=-100, max_value=100,
                            allow_nan=False, allow_infinity=False))
    scaled = [x * k for x in values]
    v_scaled = statistics.variance(scaled)
    expected = v * (k ** 2)
    scale2 = max(1.0, abs(expected))
    assert math.isclose(v_scaled, expected, rel_tol=1e-6, abs_tol=1e-6 * scale2)
# End program