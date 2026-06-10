from hypothesis import given, strategies as st, assume
import statistics
import math

# A reasonable float strategy that avoids NaN, infinity, and extreme magnitudes
# that could cause overflow when squaring/multiplying internally.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

def _not_constant(seq):
    return any(v != seq[0] for v in seq)

def _ranks(values):
    """Compute fractional ranks with ties averaged."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        # find extent of tie group
        while j + 1 < n and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # 1-based average rank
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


@given(st.data())
def test_statistics_correlation_property():
    method = st.sampled_from(['linear', 'ranked'])

    # --- Property 1: output is a float bounded within [-1, +1] ---
    n = st.integers(min_value=2, max_value=50)
    n1 = data_draw = None  # placeholder to keep structure clear

    m = data = None

    # Property 1
    chosen_method = st.data
    # draw inputs
    length = st.integers(min_value=2, max_value=50)
    L = st_draw = None

    # We use the inner draw helper from st.data via the given fixture below.
    pass


@given(
    data=st.data(),
    method=st.sampled_from(['linear', 'ranked']),
)
def test_correlation_bounded(data, method):
    # Property 1: output always a float within [-1, 1] for valid input.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    assume(_not_constant(x) and _not_constant(y))
    r = statistics.correlation(x, y, method=method)
    assert isinstance(r, float)
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9


@given(
    data=st.data(),
    method=st.sampled_from(['linear', 'ranked']),
)
def test_correlation_symmetric(data, method):
    # Property 2: correlation(x, y) == correlation(y, x).
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    assume(_not_constant(x) and _not_constant(y))
    r_xy = statistics.correlation(x, y, method=method)
    r_yx = statistics.correlation(y, x, method=method)
    assert math.isclose(r_xy, r_yx, rel_tol=1e-9, abs_tol=1e-9)


@given(
    data=st.data(),
    method=st.sampled_from(['linear', 'ranked']),
)
def test_correlation_self_and_negation(data, method):
    # Property 3: corr(x, x) == 1.0 and corr(x, -x) == -1.0.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    assume(_not_constant(x))
    neg_x = [-v for v in x]
    r_self = statistics.correlation(x, x, method=method)
    r_neg = statistics.correlation(x, neg_x, method=method)
    assert math.isclose(r_self, 1.0, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(r_neg, -1.0, rel_tol=1e-9, abs_tol=1e-9)


@given(
    data=st.data(),
    method=st.sampled_from(['linear', 'ranked']),
)
def test_correlation_affine_invariance(data, method):
    # Property 4: invariant under positive linear transforms, sign flips
    # under negative scaling.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    assume(_not_constant(x) and _not_constant(y))

    a = data.draw(st.floats(min_value=0.01, max_value=100, allow_nan=False,
                            allow_infinity=False))
    b = data.draw(st.floats(min_value=-100, max_value=100, allow_nan=False,
                            allow_infinity=False))
    base = statistics.correlation(x, y, method=method)

    # positive scaling + shift preserves correlation
    x_pos = [a * v + b for v in x]
    assume(_not_constant(x_pos))
    r_pos = statistics.correlation(x_pos, y, method=method)
    assert math.isclose(r_pos, base, rel_tol=1e-7, abs_tol=1e-7)

    # negative scaling flips the sign
    x_neg = [-a * v + b for v in x]
    assume(_not_constant(x_neg))
    r_neg = statistics.correlation(x_neg, y, method=method)
    assert math.isclose(r_neg, -base, rel_tol=1e-7, abs_tol=1e-7)


@given(
    data=st.data(),
)
def test_correlation_ranked_consistency_and_monotonic(data):
    # Property 5: ranked method equals linear on rank-transformed data;
    # strictly increasing relationship yields exactly 1.0.
    n = data.draw(st.integers(min_value=2, max_value=50))
    x = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    y = data.draw(st.lists(finite_floats, min_size=n, max_size=n))
    assume(_not_constant(x) and _not_constant(y))

    ranked = statistics.correlation(x, y, method='ranked')
    rx = _ranks(x)
    ry = _ranks(y)
    assume(_not_constant(rx) and _not_constant(ry))
    linear_on_ranks = statistics.correlation(rx, ry, method='linear')
    assert math.isclose(ranked, linear_on_ranks, rel_tol=1e-7, abs_tol=1e-7)

    # strictly increasing monotonic relationship -> 1.0
    x_sorted = sorted(set(x))
    assume(len(x_sorted) >= 2)
    y_mono = [2.0 * v + 5.0 for v in x_sorted]  # strictly increasing in x
    r_mono = statistics.correlation(x_sorted, y_mono, method='ranked')
    assert math.isclose(r_mono, 1.0, rel_tol=1e-9, abs_tol=1e-9)
# End program