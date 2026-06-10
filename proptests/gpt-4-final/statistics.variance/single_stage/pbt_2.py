from hypothesis import given, strategies as st, example
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2))
@example([])
@example([1.5])
def test_statistics_variance(l):
    if len(l) < 2:
        try:
            statistics.variance(l)
        except statistics.StatisticsError:
            pass
        else:
            assert False, "Expected StatisticsError"
    else:
        v = statistics.variance(l)
        assert isinstance(v, float), "Must return a real number"
        # Checking determinism
        v_again = statistics.variance(l)
        assert v == v_again, "Must consistently return the same result for the same input"
        
        # Checking list with similar elements
        l_same = [l[0]] * len(l)
        v_same = statistics.variance(l_same)
        assert v_same == 0.0, "The variance of a list with same elements should be zero"
    
# End program