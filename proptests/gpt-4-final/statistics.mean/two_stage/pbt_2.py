from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_single_value(l):
    # Testing property 1: Output should be a single numerical value
    assert isinstance(statistics.mean(l), float)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
def test_mean_empty_input(l):
    # Testing property 2: mean function should raise a StatisticsError for an empty input
    if not l:
        try:
            statistics.mean(l)
            assert False, "Expected StatisticsError"
        except statistics.StatisticsError:
            pass

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_reordering(l):
    # Testing property 3: The output should be same for re-ordered input data
    assert statistics.mean(l) == statistics.mean(list(reversed(l)))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_same_elements(l):
    # Testing property 4: If all elements are same, the output should be equal to that single value
    single_value = l[0]
    same_elements = [single_value] * len(l)
    assert statistics.mean(same_elements) == single_value

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_mean_double_values(l):
    # Testing property 5: Doubling all values in the input sequence should result in 2 times the mean of original input
    double_values = [2 * num for num in l]
    assert statistics.mean(double_values) == 2 * statistics.mean(l)
# End program