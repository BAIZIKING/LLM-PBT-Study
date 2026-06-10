from hypothesis import given, strategies as st
import math
import statistics

# Summary: Generate lists (>=2) of finite, bounded floats to avoid NaN/inf/overflow.
# Check non-negativity, xbar consistency, translation invariance, scaling (k^2),
# and zero variance for constant data.
@given(st.data())
def test_statistics_variance(data):
    finite_floats = st.floats(
        allow_nan=False, allow_infinity=False,
        min_value=-1e6, max_value=1e6,
    )

    drawn = data.draw(st.lists(finite_floats, min_size=2, max_size=50))

    v = statistics.variance(drawn)
    assert v >= 0 or math.isclose(v, 0.0, abs_tol=1e-9)

    m = statistics.mean(drawn)
    assert math.isclose(v, statistics.variance(drawn, m), rel_tol=1e-9, abs_tol=1e-9)

    c = data.draw(finite_floats)
    assert math.isclose(v, statistics.variance([x + c for x in drawn]),
                        rel_tol=1e-6, abs_tol=1e-6)

    k = data.draw(st.floats(allow_nan=False, allow_infinity=False,
                            min_value=-1e3, max_value=1e3))
    assert math.isclose(statistics.variance([x * k for x in drawn]),
                        v * (k ** 2), rel_tol=1e-6, abs_tol=1e-6)

    cv = data.draw(finite_floats)
    n = data.draw(st.integers(min_value=2, max_value=20))
    assert math.isclose(statistics.variance([cv] * n), 0.0, abs_tol=1e-9)
# End program