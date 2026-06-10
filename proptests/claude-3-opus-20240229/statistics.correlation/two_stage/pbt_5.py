from hypothesis import given, strategies as st
import statistics
import math

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.sampled_from(['linear', 'ranked']))
def test_correlation_range(x, method):
    r = statistics.correlation(x, x, method=method)
    assert -1.0 <= r <= 1.0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_identical_inputs(x):
    r_linear = statistics.correlation(x, x, method='linear')
    r_ranked = statistics.correlation(x, x, method='ranked')
    assert r_linear == 1.0
    assert r_ranked == 1.0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_negative_inputs(x):
    y = [-i for i in x]
    r_linear = statistics.correlation(x, y, method='linear')
    r_ranked = statistics.correlation(x, y, method='ranked')
    assert r_linear == -1.0
    assert r_ranked == -1.0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correlation_shuffled_inputs(x):
    y = list(x)
    st.random.shuffle(y)
    r_ranked = statistics.correlation(x, y, method='ranked')
    assert math.isclose(r_ranked, 1.0, rel_tol=1e-08)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), st.floats(), st.floats(min_value=0))
def test_correlation_scaled_inputs(x, scale, translate):
    y = [i * scale + translate for i in x]
    r_linear_orig = statistics.correlation(x, x, method='linear')
    r_linear_scaled = statistics.correlation(x, y, method='linear')
    r_ranked_orig = statistics.correlation(x, x, method='ranked')
    r_ranked_scaled = statistics.correlation(x, y, method='ranked')
    assert math.isclose(r_linear_orig, r_linear_scaled)
    assert math.isclose(r_ranked_orig, r_ranked_scaled)
# End program