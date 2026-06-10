from hypothesis import given, strategies as st, assume
import statistics

@given(st.lists(st.floats(min_value=1, exclude_min=True), min_size=1))
def test_returns_float(lst):
    assert isinstance(statistics.geometric_mean(lst), float)


@given(st.lists(st.floats(), min_size=1))
def test_zero_or_negative_raises(lst):
    assume(any(x <= 0 for x in lst))
    try:
        statistics.geometric_mean(lst)
    except statistics.StatisticsError:
        assert True
    else:
        assert False


@given(st.lists(st.floats(min_value=1, exclude_min=True), min_size=2))
def test_within_max_and_min_range(lst):
    result = statistics.geometric_mean(lst)
    assert min(lst) <= result <= max(lst)


@given(st.lists(st.floats(min_value=1, max_value=1, exclude_min=True), min_size=1))
def test_all_the_same_returns_same(lst):
    assert statistics.geometric_mean(lst) == lst[0]


@given(st.lists(st.floats(min_value=1, exclude_min=True), min_size=1), st.floats(min_value=1, exclude_min=True))
def test_scale_invariance(lst, scale):
    scaled_lst = [x*scale for x in lst]
    assert statistics.geometric_mean(scaled_lst) == abs(scale) * statistics.geometric_mean(lst)
# End program