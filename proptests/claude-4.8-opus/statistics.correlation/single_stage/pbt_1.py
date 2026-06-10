from hypothesis import given, strategies as st, assume
from statistics import correlation, StatisticsError
import math

# Summary: Using st.data(), draw a length n>=2, two lists of bounded finite floats,
# and a method ('linear' or 'ranked'). Properties verified:
#  (1) when inputs are valid (non-constant), result r satisfies -1 <= r <= 1;
#  (2) correlation is symmetric: corr(x,y) == corr(y,x);
#  (3) a strictly increasing positive affine transform of x gives r ~= 1.0;
#  (4) negation of x gives r ~= -1.0;
#  (5) constant inputs raise StatisticsError.
@given(st.data())
def test_statistics_correlation():
    data = st.data()
    n = data.draw(st.integers(min_value=2, max_value=30))

    finite = st.floats(min_value=-1e6, max_value=1e6,
                       allow_nan=False, allow_infinity=False)
    x = data.draw(st.lists(finite, min_size=n, max_size=n))
    y = data.draw(st.lists(finite, min_size=n, max_size=n))
    method = data.draw(st.sampled_from(['linear', 'ranked']))

    x_const = len(set(x)) == 1
    y_const = len(set(y)) == 1

    # Property (5): constant input(s) must raise StatisticsError.
    if x_const or y_const:
        try:
            correlation(x, y, method=method)
            assert False, "Expected StatisticsError for constant input"
        except StatisticsError:
            return  # nothing more to check for invalid inputs

    # Inputs are valid (non-constant, equal length >= 2).
    r = correlation(x, y, method=method)

    # Property (1): bounded in [-1, 1] (allow tiny float tolerance).
    assert -1.0 - 1e-9 <= r <= 1.0 + 1e-9

    # Property (2): symmetry of correlation.
    r_swapped = correlation(y, x, method=method)
    assert math.isclose(r, r_swapped, rel_tol=1e-9, abs_tol=1e-9)

    # Build a strictly increasing positive affine transform of x:
    # y_pos = 3*x + 7 preserves both linear and monotonic perfect correlation.
    y_pos = [3.0 * v + 7.0 for v in x]
    if len(set(y_pos)) > 1:  # ensure non-constant (true since x non-constant)
        r_pos = correlation(x, y_pos, method=method)
        # Property (3): perfect positive correlation ~ 1.0
        assert math.isclose(r_pos, 1.0, rel_tol=1e-7, abs_tol=1e-7)

    # Build negation of x:
    y_neg = [-v for v in x]
    if len(set(y_neg)) > 1:
        r_neg = correlation(x, y_neg, method=method)
        # Property (4): perfect negative correlation ~ -1.0
        assert math.isclose(r_neg, -1.0, rel_tol=1e-7, abs_tol=1e-7)
# End program