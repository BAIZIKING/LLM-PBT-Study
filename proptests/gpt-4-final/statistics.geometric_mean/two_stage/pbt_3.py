from hypothesis import given, strategies as st, assume
import statistics
import math

@given(st.lists(st.floats(min_value=1e-10, max_value=1e10), min_size=1))
def test_geometric_mean_type_property(data):
    result = statistics.geometric_mean(data)
    assert isinstance(result, float)

@given(st.lists(st.floats(min_value=1e-10, max_value=1e10), min_size=1))
def test_geometric_mean_input_output_relation(data):
    geom_mean = statistics.geometric_mean(data)
    arith_mean = sum(data) / len(data)
    assert geom_mean <= arith_mean

@given(st.lists(st.floats(), max_size=0))
def test_geometric_mean_empty_dataset(data):
    try:
        result = statistics.geometric_mean(data)
    except statistics.StatisticsError:
        assert True
    else:
        assert False

@given(st.lists(st.floats(max_value=0)))
def test_geometric_mean_non_positive_error(data):
    assume(len(data) > 0)
    try:
        result = statistics.geometric_mean(data)
    except statistics.StatisticsError:
        assert True
    else:
        assert False

@given(st.lists(st.floats(min_value=1e-10, max_value=1e10), min_size=1), st.floats(min_value=1e-10, max_value=1e10))
def test_geometric_mean_scaling_property(data, n):
    geo_mean = statistics.geometric_mean(data)
    data_scaled = [x * n for x in data]
    geo_mean_scaled = statistics.geometric_mean(data_scaled)
    assert math.isclose(geo_mean * n, geo_mean_scaled, rel_tol=1e-9)