from hypothesis import given, strategies as st, assume
import statistics

@given(
    st.tuples(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2), 
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)
    )
)
def test_statistics_correlation(t):
    assume(len(set(t[0]))>=2 and len(set(t[1]))>=2)  # ensure list is not constant
    assume(len(t[0]) == len(t[1]))  # ensure both lists are of same length
    result = statistics.correlation(t[0], t[1])
    assert isinstance(result, float)
    assert -1 <= result <= 1