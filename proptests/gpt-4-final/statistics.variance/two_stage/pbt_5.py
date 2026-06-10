from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_zero_for_identical_elements(data):
    assert statistics.variance(data) == 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_non_negative(data):
    assert statistics.variance(data) >= 0

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2).map(lambda x: sorted(x)))
def test_variance_independent_of_order(data):
    original = statistics.variance(data)
    data.reverse()
    assert original == statistics.variance(data)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_with_precomputed_mean(data):
    mean = statistics.mean(data)
    assert statistics.variance(data) == statistics.variance(data, mean)

@given(st.lists(st.decimals(allow_nan=False, allow_infinity=False), min_size=2))
def test_variance_output_same_type_decimal(data):
    assert isinstance(statistics.variance(data), type(data[0]))

@given(st.lists(st.fractions(), min_size=2))
def test_variance_output_same_type_fraction(data):
    assert isinstance(statistics.variance(data), type(data[0]))
# End program