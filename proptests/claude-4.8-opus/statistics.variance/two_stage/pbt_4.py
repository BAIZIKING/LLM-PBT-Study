from hypothesis import given, strategies as st, assume
import statistics
import math

# Strategy for real-valued floats that avoid overflow/NaN/inf issues.
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# A list of at least two such floats.
data_lists = st.lists(finite_floats, min_size=2, max_size=50)


@given(data=data_lists)
def test_statistics_variance_non_negative(data):
    # Property 1: variance is always non-negative.
    result = statistics.variance(data)
    assert result >= 0
# End program


@given(data=data_lists)
def test_statistics_variance_zero_iff_all_equal(data):
    # Property 2: variance == 0 iff all data points are identical.
    result = statistics.variance(data)
    all_equal = all(x == data[0] for x in data)
    if all_equal:
        assert result == 0
    else:
        assert result > 0
# End program


@given(data=data_lists, c=finite_floats)
def test_statistics_variance_translation_invariant(data, c):
    # Property 3: adding a constant to every element leaves variance unchanged.
    original = statistics.variance(data)
    shifted = statistics.variance([x + c for x in data])
    assert math.isclose(original, shifted, rel_tol=1e-6, abs_tol=1e-6)
# End program


@given(data=data_lists, k=st.floats(min_value=-1e3, max_value=1e3,
                                    allow_nan=False, allow_infinity=False))
def test_statistics_variance_scaling(data, k):
    # Property 4: scaling every element by k scales variance by k**2.
    original = statistics.variance(data)
    scaled = statistics.variance([x * k for x in data])
    expected = original * (k ** 2)
    assert math.isclose(scaled, expected, rel_tol=1e-6, abs_tol=1e-6)
# End program


@given(data=data_lists)
def test_statistics_variance_xbar_consistency(data):
    # Property 5: passing the correct mean as xbar yields the same result.
    auto = statistics.variance(data)
    m = statistics.mean(data)
    with_xbar = statistics.variance(data, m)
    assert math.isclose(auto, with_xbar, rel_tol=1e-9, abs_tol=1e-9)
# End program