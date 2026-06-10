from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(min_value=0.1,max_value=1000), min_size=1))
def test_return_type(data):
    assert isinstance(statistics.geometric_mean(data), float)

@given(st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1))
def test_output_range(data):
    assert statistics.geometric_mean(data) >= 0

@given(st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1))
def test_accuracy(data):
    result = round(statistics.geometric_mean(data), 1)
    assert abs(result - statistics.geometric_mean(data)) < 0.05 

@given(st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1))
def test_value_comparison(data):
    assert statistics.geometric_mean(data) <= statistics.mean(data)

@given(st.lists(st.floats(min_value=0.1, max_value=1000), min_size=1))
def test_exception_handling(data):
    try:
        statistics.geometric_mean(data + [0])
        assert False  # Expected a StatisticsError
    except statistics.StatisticsError:
        assert True
    try:
        statistics.geometric_mean(data + [-1])
        assert False  # Expected a StatisticsError
    except statistics.StatisticsError:
        assert True
    try:
        statistics.geometric_mean([])
        assert False  # Expected a StatisticsError
    except statistics.StatisticsError:
        assert True