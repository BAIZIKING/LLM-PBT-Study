from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_median_property_1(input_data):
    assert isinstance(statistics.median(input_data), (int, float))

@given(st.lists(st.integers(), min_size=3, max_size=7))
def test_median_property_2(input_data):
    if len(input_data) % 2 != 0:
        sorted_data = sorted(input_data)
        assert statistics.median(input_data) == sorted_data[len(sorted_data)//2]

@given(st.lists(st.integers(), min_size=4, max_size=8))
def test_median_property_3(input_data):
    if len(input_data) % 2 == 0:
        sorted_data = sorted(input_data)
        assert statistics.median(input_data) == (sorted_data[len(sorted_data)//2-1] + sorted_data[len(sorted_data)//2]) / 2

@given(st.lists(st.integers(min_value=1, max_value=500), min_size=5).map(lambda x: x + [10000]))
def test_median_property_4(input_data):
    assert statistics.median(input_data) <= 500

@given(st.lists(st.integers()))
def test_median_property_5(input_data):
    if not input_data:
        try:
            statistics.median(input_data)
        except StatisticsError:
            pass
        else:
            assert False, "Expected StatisticsError"
    else:
        assert isinstance(statistics.median(input_data), (int, float))
# End program