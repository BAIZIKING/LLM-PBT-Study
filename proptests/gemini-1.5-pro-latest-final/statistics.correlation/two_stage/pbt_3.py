from hypothesis import given, strategies as st
import statistics

# Define a strategy for generating lists of floats within a reasonable range
reasonable_floats = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False)

@given(st.data())
def test_correlation_output_range(data):
    x = data.draw(st.lists(reasonable_floats, min_size=2))
    y = data.draw(st.lists(reasonable_floats, min_size=2, max_size=len(x)))
    result = statistics.correlation(x, y)
    assert -1 <= result <= 1

@given(st.data())
def test_correlation_symmetry(data):
    x = data.draw(st.lists(reasonable_floats, min_size=2))
    y = data.draw(st.lists(reasonable_floats, min_size=2, max_size=len(x)))
    result1 = statistics.correlation(x, y)
    result2 = statistics.correlation(y, x)
    assert result1 == result2

@given(st.data())
def test_correlation_constant_input(data):
    constant = data.draw(reasonable_floats)
    x = [constant] * 2
    y = [constant] * 2
    with pytest.raises(statistics.StatisticsError):
        statistics.correlation(x, y)

@given(st.data())
def test_spearman_monotonic_relationship(data):
    x = data.draw(st.lists(reasonable_floats, min_size=2, unique=True))
    # Create a monotonic relationship by sorting or reversing x
    y = sorted(x) or list(reversed(x)) 
    result = statistics.correlation(x, y, method='ranked')
    assert result in (1, -1)

@given(st.data())
def test_pearson_linear_relationship(data):
    x = data.draw(st.lists(reasonable_floats, min_size=2, unique=True))
    # Create a perfect linear relationship with a random slope
    slope = data.draw(st.floats(allow_nan=False, allow_infinity=False))
    y = [slope * value + data.draw(reasonable_floats) for value in x]
    result = statistics.correlation(x, y)
    assert result in (1, -1) 

# End program