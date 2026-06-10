from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_type_consistency(data):
    result = statistics.median(data)
    if len(data) % 2 == 0:
        assert isinstance(result, float)
    else:
        assert isinstance(result, type(data[0]))

@given(st.lists(st.integers(), min_size=1))
def test_order_independence(data):
    assert statistics.median(data) == statistics.median(sorted(data))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
def test_correct_length_handling(data):
    sorted_data = sorted(data)
    if len(data) % 2 == 0:
        expected_result = (sorted_data[len(data)//2 - 1] + sorted_data[len(data)//2]) / 2
    else:
        expected_result = sorted_data[len(data)//2]
    assert statistics.median(data) == expected_result

@given(st.lists(st.text(min_size=1), min_size=1))
def test_non_numeric_input_handling(data):
    try:
        statistics.median(data)
    except TypeError as e:
        assert str(e) == "can't compare 'int' to 'str'"

@given(st.lists(st.integers(), max_size=0))
def test_empty_input_handling(data):
    try:
        statistics.median(data) 
    except statistics.StatisticsError as e:
        assert str(e) == "no median for empty data"
# End program