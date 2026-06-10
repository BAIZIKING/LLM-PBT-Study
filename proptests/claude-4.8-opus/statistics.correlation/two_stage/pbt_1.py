from hypothesis import given, strategies as st, assume
import statistics
import math

# Bounded finite floats to avoid nan/inf and overflow in sums of squares/products.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


def is_constant(seq):
    return all(v == seq[0] for v in seq)


def draw_two_sequences(data, min_size=2, max_size=50):
    n = data.draw(st.integers(min_value=min_size, max_value=max_size))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    return x, y


@given(st.data())
def test_statistics_correlation_property(data):
    # Tolerance for floating-point comparisons.
    TOL = 1e-7

    # =====================================================================
    # Property 1: Output is a float within the closed interval [-1, +1].
    # =====================================================================
    x, y = draw_two_sequences(data)
    for method in ("linear", "ranked"):
        if is_constant(x) or is_constant(y):
            # Constant input must raise StatisticsError.
            try:
                statistics.correlation(x, y, method=method)
                assert False, "Expected StatisticsError for constant input"
            except statistics.StatisticsError:
                pass
        else:
            r = statistics.correlation(x, y, method=method)
            assert isinstance(r, float)
            assert -1.0 - TOL <= r <= 1.0 + TOL

    # =====================================================================
    # Property 2: Symmetry -- correlation(x, y) == correlation(y, x).
    # =====================================================================
    if not (is_constant(x) or is_constant(y)):
        for method in ("linear", "ranked"):
            r_xy = statistics.correlation(x, y, method=method)
            r_yx = statistics.correlation(y, x, method=method)
            assert math.isclose(r_xy, r_yx, rel_tol=1e-9, abs_tol=TOL)

    # =====================================================================
    # Property 3: correlation(x, x) == +1.0 for non-constant x.
    # =====================================================================
    z = data.draw(st.lists(finite_floats, min_size=2, max_size=50))
    if not is_constant(z):
        for method in ("linear", "ranked"):
            r_self = statistics.correlation(z, z, method=method)
            assert math.isclose(r_self, 1.0, rel_tol=1e-9, abs_tol=TOL)

    # =====================================================================
    # Property 4: Invariance under positive linear transformations
    #             for the linear method:
    #             correlation(a*x + b, c*y + d) == correlation(x, y), a,c > 0.
    # =====================================================================
    if not (is_constant(x) or is_constant(y)):
        a = data.draw(st.floats(min_value=1e-3, max_value=1e3,
                                allow_nan=False, allow_infinity=False))
        c = data.draw(st.floats(min_value=1e-3, max_value=1e3,
                                allow_nan=False, allow_infinity=False))
        b = data.draw(st.floats(min_value=-1e3, max_value=1e3,
                                allow_nan=False, allow_infinity=False))
        d = data.draw(st.floats(min_value=-1e3, max_value=1e3,
                                allow_nan=False, allow_infinity=False))
        xt = [a * xi + b for xi in x]
        yt = [c * yi + d for yi in y]
        # Transformed sequences could become (numerically) constant; guard.
        if not (is_constant(xt) or is_constant(yt)):
            r_orig = statistics.correlation(x, y, method="linear")
            r_trans = statistics.correlation(xt, yt, method="linear")
            assert math.isclose(r_orig, r_trans, rel_tol=1e-6, abs_tol=1e-6)

    # =====================================================================
    # Property 5: Perfect monotonic relationships give ranked corr +/-1.0.
    #   Build strictly increasing distinct values, then y = x**3
    #   (increasing => +1.0) and y = -(x**3) (decreasing => -1.0).
    # =====================================================================
    n = data.draw(st.integers(min_value=2, max_value=30))
    # Draw n distinct values, then sort to get a strictly increasing sequence.
    distinct = data.draw(
        st.lists(
            st.floats(min_value=-1e2, max_value=1e2,
                      allow_nan=False, allow_infinity=False),
            min_size=n, max_size=n, unique=True,
        )
    )
    mono_x = sorted(distinct)
    # All distinct & sorted => strictly increasing, non-constant.
    mono_pos = [v ** 3 for v in mono_x]          # monotonically increasing
    mono_neg = [-(v ** 3) for v in mono_x]       # monotonically decreasing
    # Guard against any degenerate (constant) cube list (shouldn't happen).
    if not is_constant(mono_pos):
        r_pos = statistics.correlation(mono_x, mono_pos, method="ranked")
        assert math.isclose(r_pos, 1.0, rel_tol=1e-9, abs_tol=TOL)
    if not is_constant(mono_neg):
        r_neg = statistics.correlation(mono_x, mono_neg, method="ranked")
        assert math.isclose(r_neg, -1.0, rel_tol=1e-9, abs_tol=TOL)
# End program