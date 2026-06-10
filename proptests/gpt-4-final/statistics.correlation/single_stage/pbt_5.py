from hypothesis import given, strategies as st
import statistics

# Generation Strategy: Generate two lists of the same length with float values, and method either 'linear' or 'ranked'
@given(st.lists(st.floats(), min_size=2).flatmap(lambda x: st.tuples(st.just(x), st.lists(st.floats(), min_size=len(x), max_size=len(x)))), st.sampled_from(['linear', 'ranked']))
def test_statistics_correlation(data, method):
    x, y = data
    correlation = statistics.correlation(x, y, method=method)

    # Properties check: Correlation should return a float between -1 and 1
    assert isinstance(correlation, float)
    assert -1 <= correlation <= 1